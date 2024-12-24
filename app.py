# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
app.secret_key = 'replace_with_secure_key'

# ----------------------------
# MongoDB Setup
# ----------------------------
app.config["MONGO_URI"] = "mongodb://localhost:27017/vuluru_todo"
mongo = PyMongo(app)

tasks_collection = mongo.db.tasks
contacts_collection = mongo.db.contacts

valid_task_sort_fields = {
    "due_date": "due_date",
    "priority": "priority"
}

# ----------------------------
# 1. Home
# ----------------------------
@app.route('/')
def home():
    return render_template('home.html')

# ----------------------------
# 2. Tasks (List)
# ----------------------------
@app.route('/tasks')
def tasks_index():
    filter_status = request.args.get('filter_status', 'All')
    sort_by = request.args.get('sort_by', 'due_date')
    sort_order = request.args.get('sort_order', 'Descending')

    query = {}
    if filter_status != 'All':
        query['status'] = filter_status

    sort_dir = -1 if sort_order == 'Descending' else 1
    db_sort_field = valid_task_sort_fields.get(sort_by, 'due_date')
    
    try:
        tasks = list(tasks_collection.find(query).sort(db_sort_field, sort_dir))
    except Exception as e:
        flash(f"Error fetching tasks: {e}", "danger")
        tasks = []

    return render_template('tasks.html',
                           tasks=tasks,
                           filter_status=filter_status,
                           sort_by=sort_by,
                           sort_order=sort_order)

# ----------------------------
# 3. Add Task
# ----------------------------
@app.route('/tasks/add', methods=['GET','POST'])
def add_task():
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        due_date = request.form.get('due_date', '').strip()
        priority = request.form.get('priority', '').strip()
        status = "Pending"
        assigned_contact_id = request.form.get('assigned_contact', '')  # from dropdown

        if not description:
            flash("Task description cannot be empty.", "danger")
            return redirect(url_for('add_task'))

        if due_date:
            try:
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('add_task'))

        task_doc = {
            "description": description,
            "due_date": due_date if due_date else None,
            "priority": priority if priority else "",
            "status": status,
            "created_at": datetime.datetime.utcnow()
        }

        # if assigned_contact_id is not blank, find that contact and store name
        if assigned_contact_id:
            contact = contacts_collection.find_one({"_id": ObjectId(assigned_contact_id)})
            if contact:
                task_doc["assigned_contact_id"] = assigned_contact_id
                task_doc["assigned_contact_name"] = contact.get("name", "Unknown")

        try:
            tasks_collection.insert_one(task_doc)
            flash("Task added successfully!", "success")
            return redirect(url_for('tasks_index'))
        except Exception as e:
            flash(f"Error adding task: {e}", "danger")
            return redirect(url_for('add_task'))
    else:
        # GET -> show form + fetch contacts for dropdown
        contacts = list(contacts_collection.find())
        return render_template('add_task.html', contacts=contacts)

# ----------------------------
# 4. Mark Task Completed
# ----------------------------
@app.route('/tasks/complete/<task_id>', methods=['POST'])
def complete_task(task_id):
    try:
        tasks_collection.update_one({"_id": ObjectId(task_id)},
                                    {"$set": {"status": "Completed"}})
        flash("Task marked as completed!", "success")
    except Exception as e:
        flash(f"Error marking task as completed: {e}", "danger")

    return redirect(url_for('tasks_index'))

# ----------------------------
# 5. Remove Task
# ----------------------------
@app.route('/tasks/remove/<task_id>', methods=['POST'])
def remove_task(task_id):
    try:
        tasks_collection.delete_one({"_id": ObjectId(task_id)})
        flash("Task removed!", "success")
    except Exception as e:
        flash(f"Error removing task: {e}", "danger")

    return redirect(url_for('tasks_index'))

# ----------------------------
# 6. Edit Task
# ----------------------------
@app.route('/tasks/edit/<task_id>', methods=['GET','POST'])
def edit_task(task_id):
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        due_date = request.form.get('due_date', '').strip()
        priority = request.form.get('priority', '').strip()
        status = request.form.get('status', '').strip()
        assigned_contact_id = request.form.get('assigned_contact', '')

        if not description:
            flash("Task description cannot be empty.", "danger")
            return redirect(url_for('edit_task', task_id=task_id))

        if due_date:
            try:
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('edit_task', task_id=task_id))

        update_fields = {
            "description": description,
            "due_date": due_date if due_date else None,
            "priority": priority if priority else "",
            "status": status if status else "Pending"
        }

        if assigned_contact_id:
            contact = contacts_collection.find_one({"_id": ObjectId(assigned_contact_id)})
            if contact:
                update_fields["assigned_contact_id"] = assigned_contact_id
                update_fields["assigned_contact_name"] = contact.get("name", "Unknown")
            else:
                update_fields["assigned_contact_id"] = None
                update_fields["assigned_contact_name"] = None
        else:
            update_fields["assigned_contact_id"] = None
            update_fields["assigned_contact_name"] = None

        try:
            tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_fields})
            flash("Task updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating task: {e}", "danger")

        return redirect(url_for('tasks_index'))
    else:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for('tasks_index'))

        contacts = list(contacts_collection.find())
        return render_template('edit_task.html', task=task, contacts=contacts)

# ----------------------------
# 7. Contacts
# ----------------------------
@app.route('/contacts')
def contacts_index():
    contacts = list(contacts_collection.find())
    return render_template('contacts.html', contacts=contacts)

@app.route('/contacts/add', methods=['GET','POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name:
            flash("Contact name cannot be empty.", "danger")
            return redirect(url_for('add_contact'))

        contact_doc = {
            "name": name,
            "email": email,
            "phone": phone
        }
        try:
            contacts_collection.insert_one(contact_doc)
            flash("Contact added!", "success")
            return redirect(url_for('contacts_index'))
        except Exception as e:
            flash(f"Error adding contact: {e}", "danger")
            return redirect(url_for('add_contact'))
    else:
        return render_template('add_contact.html')

@app.route('/contacts/edit/<contact_id>', methods=['GET','POST'])
def edit_contact(contact_id):
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not name:
            flash("Contact name cannot be empty.", "danger")
            return redirect(url_for('edit_contact', contact_id=contact_id))

        update_fields = {
            "name": name,
            "email": email,
            "phone": phone
        }
        try:
            contacts_collection.update_one({"_id": ObjectId(contact_id)}, {"$set": update_fields})
            flash("Contact updated!", "success")
        except Exception as e:
            flash(f"Error updating contact: {e}", "danger")

        return redirect(url_for('contacts_index'))
    else:
        contact = contacts_collection.find_one({"_id": ObjectId(contact_id)})
        if not contact:
            flash("Contact not found.", "danger")
            return redirect(url_for('contacts_index'))

        return render_template('edit_contact.html', contact=contact)

if __name__ == '__main__':
    app.run(debug=True)