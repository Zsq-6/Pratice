from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# import tenants
import random
import string
from flask_migrate import Migrate

app = Flask(__name__)
# app.register_blueprint(tenants,url_prefix='/tenants')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/zsq/PycharmProjects/pythonProject6/managesystem/sqlite3.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/tenants'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)


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
#     # 项目相关配置
#     # projectconfigs = db.relationship('ProjectConfig', backref='projects', lazy='dynamic')
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
    # project_id = db.relationship(db.String(128), db.ForeignKey('project.id'))
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
        }

@app.route('/tenants', methods=['POST'])
# 创建租户，租户名唯一不可重复
def create_tenant():
    name = request.json.get('name')
    if name is None or name == '':
        return jsonify({'success':False,'error_code':0, 'errmsg':'缺少租户名字'})
    if not name.isalnum():
        return jsonify({'success':False, 'error_code':0, 'errmsg':'租户名只能为英文加数字'})
    name.lower()
    print(name)
    if Tenant.query.filter_by(name=name).first() is not None:
        return jsonify({'success':False,'error_code':0,'errmsg':'租户名已经存在'})


    describe = request.json.get('describe')
    ouid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    createdat = request.json.get('createdat')
    updatedat = request.json.get('updatedat')
    # tenant_id = request.json.get('tenant_id')
    # tenant = Tenant.query.filter_by(id=tenant_id).first()
    tenant = Tenant(name=name, describe=describe, ouid=ouid,createdat=createdat,updatedat=updatedat)
    print('---------------')
    print(name, describe, ouid)
    db.session.add(tenant)
    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "name": name,
            "ouid": ouid,
            "describe": describe,
        }
    })


@app.route('/tenants/<int:id>', methods=['PUT'])
def modify_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    name = request.json.get('name')
    desribe = request.json.get('describe')
    updatedat = request.json.get('updatedat')
    tenant.name = name or tenant.name
    tenant.describe = desribe or tenant.describe
    tenant.updatedat = updatedat or tenant.updatedat

    db.session.add(tenant)
    db.session.commit()

    return jsonify({'success':True,
                    'error_code':0,
                    })


@app.route('/tenants/delete/<int:id>', methods=['DELETE'])
def delete_tenant(id):
    tenant = Tenant.query.get(id)
    if tenant is None:
        return jsonify({'success':False, 'error_code':0, 'errmsg':'租户不存在'})
    db.session.delete(tenant)
    db.session.commit()

    return jsonify({
                    'success':True,
                    'error_code':0
                    })


@app.route('/tenants', methods=['GET'])
def get_tenants():
    tenants = Tenant.query.all()
    return jsonify({'success':False,
        'data': [tenant.to_json() for tenant in tenants]})










@app.route('/projects', methods=['GET'])
def get_project():
    projects = Project.query.all()
    return jsonify({'success':True,
                    'data':[project.to_json() for project in projects]})





@app.route('/projects', methods=['POST'])
def create_project():
    name = request.json.get('name')
    if name is None and name == '':
        return jsonify({'ret':False, 'error_code':0, 'errmsg': '项目名不能为空'})
    if Project.query.filter_by(name=name).first() is not None:
        return jsonify({'ret':False, 'error_code':10000, 'errmsg': '项目名字重复'})
    describe = request.json.get('describe')
    print(describe)
    puid = request.json.get('puid')
    createdat = request.json.get('createdat')
    updatedat = request.json.get('updatedat')
    tenant_id = request.json.get('tenant_id')

    project = Project(name=name,describe=describe,puid=puid,createdat=createdat,updatedat=updatedat,tenant_id=tenant_id)
    # print('------------------')
    # print(name, describe, createdat)
    db.session.add(project)
    db.session.commit()

    return jsonify({
        'success':True,
        'data':{
            'name': name,
            'puid': puid,
            'describe': describe,
            'tenant_id': tenant_id,
            }
        })



@app.route('/projects/<int:id>', methods=['PUT'])
def modify_project(id):
    project = Project.query.get_or_404(id)
    name = request.json.get('name')
    describe = request.json.get('describe')
    updatedat = request.json.get('updatedat')
    project.name = name or project.name
    project.describe = describe or project.describe
    project.updatedat = updatedat or project.updatedat

    db.session.commit()

    return jsonify({'success':True,
                    'error_code':0,
                    })


@app.route('/projects/delete/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get(id)
    if project is None:
        return jsonify({'success': False, 'error_code': 0, 'errmsg':'该项目不存在'})
    db.session.delete(project)
    db.session.commit()

    return jsonify({
        'success':True,
        'error_code':0
    })












@app.route('/config', methods=['GET'])
def get_projectconfig():
    projectconfigs = ProjectConfig.query.all()

    return jsonify({'success':True,
                    'data':[projectconfig .to_json() for projectconfig in projectconfigs],
                    })



@app.route('/config', methods=['POST'])
def creat_projectconfig():
    name = request.json.get('name')
    value = request.json.get('value')     # 备注
    puid = request.json.get('puid')
    createdat = request.json.get('createdat')
    updatedat = request.json.get('updatedat')

    projectconfig = ProjectConfig(name=name,value=value,puid=puid,createdat=createdat,updatedat=updatedat)

    db.session.add(projectconfig)
    db.session.commit()


    return jsonify({
                    'success':True,
                    'data':{
                        'name':name,
                        'puid':puid,
                        'value':value,
                        }
                    })

@app.route('/config/<int:id>', methods=['PUT'])
def modify_projectconfig(id):
    projectconfig = ProjectConfig.query.get_or_404(id)
    name = request.json.get('name')
    value = request.json.get('value')
    createdat = request.json.get('createdat')
    updatedat = request.json.get('updatedat')
    projectconfig.name  = name or projectconfig.name
    projectconfig.value = value or projectconfig.value
    projectconfig.createdat = createdat or projectconfig.createdat
    projectconfig.updatedat = updatedat or projectconfig.updatedat

    db.session.commit()

    return jsonify({
                    'success':True,
                    'error_code':0,
                    })




@app.route('/config/delete/<int:id>', methods=['DELETE'])
def delete_projectconfig(id):
    projectconfig = ProjectConfig.query.get(id)
    if projectconfig is None:
        return jsonify({'success':False, 'error_code':0, 'errmsg':'项目配置不存在'})
    db.session.delete(projectconfig)
    db.session.commit()

    return jsonify({
        'success':True,
        'error_code':0
    })



if __name__ == '__main__':
    app.run(debug=True)