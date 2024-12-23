# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure value in production

# ----------------------------
# MongoDB Configuration
# ----------------------------
app.config["MONGO_URI"] = "mongodb://localhost:27017/vuluru_todo"  # Update as needed
mongo = PyMongo(app)
tasks_collection = mongo.db.tasks

# Priority is stored as "High", "Medium", or "Low".
# Sorting by "priority" is purely alphabetical.
valid_sort_fields = {
    "created_at": "created_at",
    "due_date": "due_date",
    "priority": "priority"
}

# ----------------------------
# 1. Index Route (Displays Tasks)
# ----------------------------
@app.route('/')
def index():
    """
    Displays tasks with an optional filter by status 
    and sorting by date or priority (alphabetical).
    """
    try:
        filter_status = request.args.get('filter_status', 'All')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'Descending')

        query = {}
        if filter_status != 'All':
            query['status'] = filter_status

        sort_dir = DESCENDING if sort_order == 'Descending' else ASCENDING
        db_sort_field = valid_sort_fields.get(sort_by, 'created_at')

        tasks = list(tasks_collection.find(query).sort(db_sort_field, sort_dir))

        return render_template('index.html',
                               tasks=tasks,
                               filter_status=filter_status,
                               sort_by=sort_by,
                               sort_order=sort_order)
    except Exception as e:
        flash(f"An error occurred while fetching tasks: {e}", "danger")
        return render_template('index.html',
                               tasks=[],
                               filter_status='All',
                               sort_by='created_at',
                               sort_order='Descending')

# ----------------------------
# 2. Add Task (GET + POST)
# ----------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_task():
    """
    Renders the 'Add New Task' form (GET).
    Submits via a normal POST to insert a new task.
    """
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        due_date = request.form.get('due_date', '').strip()
        priority = request.form.get('priority', '').strip()  # "High"/"Medium"/"Low"

        if not description:
            flash("Task description cannot be empty.", "danger")
            return redirect(url_for('add_task'))

        # Validate date if provided
        if due_date:
            try:
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('add_task'))

        # Validate priority
        if priority not in ["High", "Medium", "Low", ""]:
            flash("Priority must be High, Medium, or Low.", "danger")
            return redirect(url_for('add_task'))

        task_doc = {
            "description": description,
            "status": "Pending",
            "due_date": due_date if due_date else None,
            "priority": priority,
            "created_at": datetime.datetime.utcnow()
        }

        try:
            tasks_collection.insert_one(task_doc)
            flash("Task added successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"An error occurred while adding the task: {e}", "danger")
            return redirect(url_for('add_task'))

    # GET request -> render the form
    return render_template('add_task.html')

# ----------------------------
# 3. Complete Task
# ----------------------------
@app.route('/complete/<task_id>', methods=['POST'])
def complete_task_route(task_id):
    """
    Marks a task as completed, sets status to 'Completed'.
    """
    try:
        tasks_collection.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': {'status': 'Completed'}}
        )
        flash("Task marked as completed!", "success")
    except Exception as e:
        flash(f"An error occurred while updating the task: {e}", "danger")

    return redirect(url_for('index'))

# ----------------------------
# 4. Remove Task
# ----------------------------
@app.route('/remove/<task_id>', methods=['POST'])
def remove_task_route(task_id):
    """
    Removes a task from the DB by _id.
    """
    try:
        tasks_collection.delete_one({'_id': ObjectId(task_id)})
        flash("Task removed successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while removing the task: {e}", "danger")

    return redirect(url_for('index'))

# ----------------------------
# 5. Edit Task (GET + POST)
# ----------------------------
@app.route('/edit/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """
    Allows editing an existing task's description, status, priority, due date.
    GET: Render edit_task.html with existing data.
    POST: Update DB, then redirect.
    """
    if request.method == 'POST':
        # Grab user input
        description = request.form.get('description', '').strip()
        status = request.form.get('status', '').strip()  # "Pending"/"Completed" 
        priority = request.form.get('priority', '').strip()
        due_date = request.form.get('due_date', '').strip()

        # Validation
        if not description:
            flash("Description cannot be empty.", "danger")
            return redirect(url_for('edit_task', task_id=task_id))

        if due_date:
            try:
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                flash("Invalid date format (YYYY-MM-DD).", "danger")
                return redirect(url_for('edit_task', task_id=task_id))

        if priority not in ["High", "Medium", "Low", ""]:
            flash("Priority must be High, Medium, or Low.", "danger")
            return redirect(url_for('edit_task', task_id=task_id))

        if status not in ["Pending", "Completed", ""]:
            flash("Status must be Pending or Completed.", "danger")
            return redirect(url_for('edit_task', task_id=task_id))

        # Build update fields
        update_fields = {
            "description": description,
            "status": status if status else "Pending",
            "priority": priority if priority else "",
            "due_date": due_date if due_date else None
        }

        try:
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_fields}
            )
            flash("Task updated successfully!", "success")
        except Exception as e:
            flash(f"An error occurred while updating: {e}", "danger")

        return redirect(url_for('index'))

    else:
        # GET -> retrieve current doc
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for('index'))

        return render_template('edit_task.html', task=task)

# ----------------------------
# Run Application
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)