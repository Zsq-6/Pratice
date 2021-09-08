from managesystem import db
from datetime import datetime

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    describe = db.Column(db.Text)                # 备注
    ouid = db.Column(db.String(128), nullable=False)
    createdat = db.Column(db.DateTime(), default=datetime.utcnow)
    updatedat = db.Column(db.DateTime(), default=datetime.utcnow)
    projects = db.relationship('Project', backref=db.backref('tenant', lazy=True))


    def to_json(self):
        return{
            'id':self.id,
            'name':self.name,
            'ouid':self.ouid,
            'describe':self.describe,
            'createdat':self.createdat,
            'updatedat':self.updatedat,
        }

    def __repr__(self):
        return '<Tenant %r>' % self.name

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    describe = db.Column(db.Text)                    # 项目备注
    # 项目ID
    puid = db.Column(db.String(128), unique=True)
    # 项目所属租户
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    createdat = db.Column(db.DateTime(), default=datetime.utcnow)
    updatedat = db.Column(db.DateTime(), default=datetime.utcnow)
    # 项目相关配置
    projectconfigs = db.relationship('ProjectConfig', backref='project', lazy=True)
    def to_json(self):
        return{
            'id':self.id,
            'name':self.name,
            'puid':self.puid,
            'describe':self.describe,
            'createdat':self.createdat,
            'updatedat':self.updatedat,
            'tenant_id':self.tenant_id,
        }

    def __repr__(self):
        return '<Project %r>' % self.describe




class ProjectConfig(db.Model):
    __tablename__ = 'projectconfigs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    value = db.Column(db.Text)               # 备注
    puid = db.Column(db.String(128))
    # 配置所属的项目
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    createdat = db.Column(db.DateTime(), default=datetime.utcnow)
    updatedat = db.Column(db.DateTime(), default=datetime.utcnow)

    def to_json(self):
        return{
            'id':self.id,
            'name':self.name,
            'value':self.value,
            'puid':self.puid,
            'createdat':self.createdat,
            'updatedat':self.updatedat,
            'project_id':self.project_id,
        }