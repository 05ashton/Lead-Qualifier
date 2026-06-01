import os
import json
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson.objectid import ObjectId
import ai_service 

app = Flask(__name__, template_folder='../frontend_dir', static_folder='../frontend_dir/static')

# 1. Connect to MongoDB
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://db:27017/lead_db")
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = mongo_client.get_database()
    leads_collection = db.leads  
except Exception as e:
    print(f"MongoDB initialization error: {e}")

# --- HTML ROUTE ---
@app.route('/')
def home():
    return render_template('index.html')


# --- REST API ROUTES ---

@app.route('/api/leads', methods=['POST'])
def create_lead():
    data = request.json
    raw_notes = data.get('raw_notes', '')
    
    ai_response = ai_service.qualify_lead(raw_notes)
    
    try:
        structured_data = json.loads(ai_response)
    except:
        return jsonify({"error": "AI did not return valid JSON"}), 500
        
    new_lead = {
        "name": data.get('name', 'Unknown'),
        "company": data.get('company', 'Unknown'),
        "raw_notes": raw_notes,
        "budget": structured_data.get('budget'),
        "authority": structured_data.get('authority'),
        "need": structured_data.get('need'),
        "timeline": structured_data.get('timeline'),
        "temperature_score": structured_data.get('temperature_score'),
        "recommended_action": structured_data.get('recommended_action'), # <-- ADD THIS LINE
        "is_active": True
    }
    
    result = leads_collection.insert_one(new_lead)
    new_lead['_id'] = str(result.inserted_id) 
    
    return jsonify(new_lead), 201


@app.route('/api/leads', methods=['GET'])
def get_leads():
    leads = []
    # FIX: Return ALL leads (both active and soft-deleted) so the frontend can sort them
    for lead in leads_collection.find():
        lead['_id'] = str(lead['_id']) 
        leads.append(lead)
    return jsonify(leads), 200


@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    data = request.json
    new_score = data.get('temperature_score')
    
    leads_collection.update_one(
        {'_id': ObjectId(lead_id)},
        {'$set': {'temperature_score': new_score}}
    )
    return jsonify({"message": "Lead updated successfully"}), 200


@app.route('/api/leads/<lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    # NEW: We no longer use .delete_one(). We just update the flag to hide it.
    leads_collection.update_one(
        {'_id': ObjectId(lead_id)},
        {'$set': {'is_active': False}}
    )
    return jsonify({"message": "Lead soft deleted successfully"}), 200


# NEW ROUTE: The Undo Button Endpoint
@app.route('/api/leads/<lead_id>/restore', methods=['PUT'])
def restore_lead(lead_id):
    leads_collection.update_one(
        {'_id': ObjectId(lead_id)},
        {'$set': {'is_active': True}}
    )
    return jsonify({"message": "Lead restored successfully"}), 200


# NEW ROUTE: Append notes and ask AI to re-evaluate
@app.route('/api/leads/<lead_id>/re-evaluate', methods=['PUT'])
def reevaluate_lead(lead_id):
    data = request.json
    new_notes = data.get('new_notes', '')
    
    # 1. Find the existing lead in the database
    existing_lead = leads_collection.find_one({'_id': ObjectId(lead_id)})
    if not existing_lead:
        return jsonify({"error": "Lead not found"}), 404
        
    # 2. Combine the old notes with the new notes
    combined_notes = existing_lead.get('raw_notes', '') + "\n\n[UPDATE]: " + new_notes
    
    # 3. Send the entire combined history back to the open-source AI
    ai_response = ai_service.qualify_lead(combined_notes)
    
    try:
        structured_data = json.loads(ai_response)
    except:
        return jsonify({"error": "AI did not return valid JSON"}), 500
        
    # 4. Save the new notes and overwrite the old AI analysis with the fresh data
    update_fields = {
        "raw_notes": combined_notes,
        "budget": structured_data.get('budget'),
        "authority": structured_data.get('authority'),
        "need": structured_data.get('need'),
        "timeline": structured_data.get('timeline'),
        "temperature_score": structured_data.get('temperature_score'),
        "recommended_action": structured_data.get('recommended_action') # <-- ADD THIS LINE
    }
    
    leads_collection.update_one(
        {'_id': ObjectId(lead_id)},
        {'$set': update_fields}
    )
    
    return jsonify({"message": "Lead re-evaluated successfully"}), 200

@app.route('/api/leads/<lead_id>/draft_email', methods=['POST'])
def draft_email(lead_id):
    lead = leads_collection.find_one({'_id': ObjectId(lead_id)})
    if not lead:
        return jsonify({"error": "Lead not found"}), 404

    # The strict multipurpose formula prompt
    prompt = f"""
    Write a short cold email to {lead.get('name')} at {lead.get('company')}.
    You MUST strictly follow this formula:
    1. Greeting.
    2. Reference their specific Need: {lead.get('need')}.
    3. Insert the exact text: "[INSERT YOUR CUSTOM SOLUTION HERE]".
    4. Call to action based on their Timeline: {lead.get('timeline')}.
    
    Do not add fluff. Output ONLY the email text.
    """
    
    response = ai_service.client.chat(
        model=ai_service.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.4} # slightly higher temp for writing creativity
    )
    
    return jsonify({"email": response['message']['content']}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)