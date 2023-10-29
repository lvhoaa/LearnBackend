from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table=db.Table(
    'association',
    db.Column('task_id',db.Integer, db.ForeignKey('task.id')),
    db.Column('category_id',db.Integer,db.ForeignKey('category.id'))
)

# implement database model classes
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String,nullable = False)
    done = db.Column(db.Boolean,nullable = False)
    # in ORM: foreigned key also must declare --> easier to retrieve 
    subtasks =db.relationship('Subtask',cascade = 'delete')
    # if delete task -> will delete subtask as well; BUT not delete the category 
    categories = db.relationship('Category',secondary=association_table,back_populates='tasks')
    
    def __init__(self,**kwargs):
        # kwargs: put ton of parameters in dictionary 
        self.description = kwargs.get('description')
        self.done = kwargs.get('done')
        
    def serialize(self):
        # return into a dictionary 
        return({
            'id':self.id,
            'description':self.description,
            'done':self.done,
            'subtasks':[s.serialize() for s in self.subtasks],
            'categories':[c.serialize() for c in self.categories]
        })

class Subtask(db.Model):
    __tablename__='subtask'
    id=db.Column(db.Integer,primary_key=True)
    description = db.Column(db.String,nullable=False)
    done=db.Column(db.Boolean,nullable=False)
    task_id = db.Column(db.Integer,db.ForeignKey('task.id'),nullable = False)
    
    def __init__(self,**kwargs):
        self.description = kwargs.get('description')
        self.done = kwargs.get('done')
        self.task_id = kwargs.get('task_id')
    
    def serialize(self):
        return {
            'id':self.id,
            'description':self.description,
            'done':self.done,
            'task_id':self.task_id
        }
     
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer,primary_key=True)
    description = db.Column(db.String,nullable = False )
    color = db.Column(db.String,nullable = True)
# first relationship: Task; second relationship: association table; back_populate: adjust accordingly with categories
    tasks = db.relationship('Task',secondary =association_table,back_populates='categories')
    
     
    def __init__(self,**kwargs):
        self.id = kwargs.get('id')
        self.description = kwargs.get('description')
        self.color = kwargs.get('color')
        
    def serialize(self):
        return {
            'id':self.id,
            'description':self.description,
            'color':self.color
        }
    
    