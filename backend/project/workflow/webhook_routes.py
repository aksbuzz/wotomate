# from flask import Blueprint, request, jsonify, current_app, json
# from .. import db
# from ..models import Workflow
# from ..enums import TriggerType
# from ..tasks import execute_workflow_task
# import jsonschema

# webhook_bp = Blueprint('webhook_bp', __name__)

# @webhook_bp.route('/<string:webhook_id>/trigger', methods=['POST'])
# def handle_inbound_webhook(webhook_id):
#     workflow = Workflow.query.filter_by(webhook_id=webhook_id, trigger_type=TriggerType.WEBHOOK_INBOUND, is_active=True).first()

#     if not workflow:
#         current_app.logger.warning(f"No active WEBHOOK_INBOUND workflow found for webhook_id: {webhook_id}")
#         return jsonify({"msg": "Workflow not found or inactive"}), 404
    
#     trigger_data = {}
#     if request.is_json:
#         trigger_data['body'] = request.get_json()
#     elif request.form:
#         trigger_data['form'] = request.form.to_dict(flat=True)
#     elif request.data:
#         try:
#             content_type = request.headers.get('Content-Type', '')
#             decoded_data = request.data.decode('utf-8')
#             if 'application/json' in content_type:
#                 trigger_data['body'] = json.loads(decoded_data)
#             else:
#                 trigger_data['body'] = decoded_data
#         except Exception as e:
#             current_app.logger.error(f"Error decoding request data: {str(e)}")
#             return jsonify({"msg": "Invalid request data"}), 400
        
#     trigger_data['headers'] = dict(request.headers)
#     trigger_data['method'] = request.method
#     trigger_data['args'] = request.args.to_dict()

#     schema = (workflow.trigger_config or {}).get('schema')
#     if schema and 'body' in trigger_data:
#         try:
#             jsonschema.validate(instance=trigger_data['body'], schema=schema)
#         except jsonschema.ValidationError as e:
#             current_app.logger.error(f"Webhook data validation failed: {str(e)}")
#             return jsonify({"msg": "Invalid webhook data", "error": str(e)}), 400

#     task = execute_workflow_task.delay(workflow.id, trigger_data)
#     current_app.logger.info(f"WEBHOOK_INBOUND trigger for workflow {workflow.id} (webhook {webhook_id}) sent to Celery {task.id}")

#     return jsonify({
#         "msg": "Webhook received, processing workflow", 
#         "task_id": task.id,
#         "workflow_id": workflow.id
#     }), 202
