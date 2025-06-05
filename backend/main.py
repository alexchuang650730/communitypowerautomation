import os
from flask import Flask, jsonify
from flask_cors import CORS

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 导入路由蓝图
try:
    # 尝试使用绝对导入
    from backend.routes.general_agent_routes import general_agent_bp
    from backend.routes.web_agent_routes import web_agent_bp
    from backend.routes.ppt_agent_routes import ppt_agent_bp
    from backend.routes.code_agent_routes import code_agent_bp
except ImportError:
    # 如果绝对导入失败，尝试相对导入
    try:
        from routes.general_agent_routes import general_agent_bp
        from routes.web_agent_routes import web_agent_bp
        from routes.ppt_agent_routes import ppt_agent_bp
        from routes.code_agent_routes import code_agent_bp
    except ImportError:
        print("警告: 导入路由模块失败，请使用项目根目录下的run_backend.py启动应用")

# 注册蓝图
try:
    app.register_blueprint(general_agent_bp, url_prefix='/api/general')
    app.register_blueprint(web_agent_bp, url_prefix='/api/web')
    app.register_blueprint(ppt_agent_bp, url_prefix='/api/ppt')
    app.register_blueprint(code_agent_bp, url_prefix='/api/code')
except NameError:
    print("警告: 无法注册蓝图，请使用项目根目录下的run_backend.py启动应用")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "PowerAutomation API服务正常运行"})

if __name__ == '__main__':
    print("警告: 直接运行main.py可能导致导入错误")
    print("建议: 请使用项目根目录下的run_backend.py启动应用")
    app.run(debug=True, host='0.0.0.0', port=5000)
