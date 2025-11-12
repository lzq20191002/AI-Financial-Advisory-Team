import os
import json
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 导入工具和代理
from tools.financial_data_tools import FinancialDataTools
from tools.analysis_tools import AnalysisTools
from agents.query_agent import QueryAgent
from agents.media_agent import MediaAgent
from agents.insight_agent import InsightAgent
from agents.report_agent import ReportAgent
from models.forum_engine import ForumEngine

# 创建Flask应用
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

# 确保报告目录存在
if not os.path.exists('reports'):
    os.makedirs('reports')

if not os.path.exists('static/charts'):
    os.makedirs('static/charts')

# 初始化工具
financial_tools = FinancialDataTools()
analysis_tools = AnalysisTools()

# 初始化代理
query_agent = QueryAgent(financial_tools)
media_agent = MediaAgent(analysis_tools)
insight_agent = InsightAgent(analysis_tools)
report_agent = ReportAgent()

# 初始化论坛协调引擎
forum_engine = ForumEngine(query_agent, media_agent, insight_agent, report_agent)

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html', title='金融市场分析系统')

@app.route('/api/analyze', methods=['POST'])
def analyze_market():
    """市场分析API"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': '缺少必要参数: query'}), 400
        
        # 获取用户查询和可选的用户画像
        user_query = data['query']
        user_profile = data.get('user_profile', None)
        
        logger.info(f"接收到分析请求: {user_query}")
        logger.info(f"用户画像: {user_profile}")
        
        # 使用论坛引擎处理查询
        result = forum_engine.process_query(user_query, user_profile)
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock_price', methods=['GET'])
def get_stock_price():
    """获取股票价格API"""
    try:
        ticker = request.args.get('ticker')
        if not ticker:
            return jsonify({'error': '缺少必要参数: ticker'}), 400
        
        days = request.args.get('days', 30, type=int)
        
        # 使用financial_tools获取股票价格
        price_data = financial_tools.get_stock_price(ticker, days)
        
        return jsonify({
            'success': True,
            'data': price_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market_news', methods=['GET'])
def get_market_news():
    """获取市场新闻API"""
    try:
        keyword = request.args.get('keyword', '')
        
        # 使用financial_tools获取市场新闻
        news_data = financial_tools.get_market_news(keyword)
        
        return jsonify({
            'success': True,
            'data': news_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market_indexes', methods=['GET'])
def get_market_indexes():
    """获取市场指数API"""
    try:
        # 使用financial_tools获取市场指数
        indexes_data = financial_tools.get_market_indexes()
        
        return jsonify({
            'success': True,
            'data': indexes_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """生成分析报告API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        # 确保必要的数据字段存在
        required_fields = ['query_data', 'analysis_results', 'insights']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
        
        query_data = data['query_data']
        analysis_results = data['analysis_results']
        insights = data['insights']
        user_profile = data.get('user_profile', None)
        
        # 使用report_agent生成报告
        report_result = report_agent.generate_report(
            query_data, 
            analysis_results, 
            insights, 
            user_profile
        )
        
        return jsonify({
            'success': True,
            'data': report_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/reports/<report_id>')
def get_report(report_id):
    """获取报告文件"""
    try:
        report_dir = os.path.join(os.getcwd(), 'reports')
        report_path = os.path.join(report_dir, f"{report_id}.html")
        
        if not os.path.exists(report_path):
            return jsonify({'error': '报告不存在'}), 404
        
        # 返回HTML报告
        return send_from_directory(report_dir, f"{report_id}.html")
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user_profile/save', methods=['POST'])
def save_user_profile():
    """保存用户画像"""
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({'error': '缺少用户ID'}), 400
        
        user_id = data['user_id']
        profile_data = data.get('profile', {})
        
        # 确保用户数据目录存在
        if not os.path.exists('user_data'):
            os.makedirs('user_data')
        
        # 保存用户画像
        with open(f'user_data/{user_id}.json', 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': '用户画像保存成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user_profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """获取用户画像"""
    try:
        profile_path = f'user_data/{user_id}.json'
        
        if not os.path.exists(profile_path):
            return jsonify({
                'success': False,
                'error': '用户画像不存在',
                'profile': None
            }), 404
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        
        return jsonify({
            'success': True,
            'profile': profile_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/status')
def system_status():
    """系统状态API"""
    try:
        # 检查各个组件的状态
        status = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0.0',
            'components': {
                'financial_tools': 'active',
                'analysis_tools': 'active',
                'query_agent': 'active',
                'media_agent': 'active',
                'insight_agent': 'active',
                'report_agent': 'active',
                'forum_engine': 'active'
            },
            'available_apis': {
                'analyze_market': '/api/analyze',
                'get_stock_price': '/api/stock_price',
                'get_market_news': '/api/market_news',
                'get_market_indexes': '/api/market_indexes',
                'generate_report': '/api/generate_report',
                'save_user_profile': '/api/user_profile/save',
                'get_user_profile': '/api/user_profile/<user_id>',
                'system_status': '/api/system/status'
            }
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '请求的资源不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    # 设置主机和端口
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 启动Flask应用
    logger.info(f"启动金融市场分析系统服务...")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"调试模式: {debug}")
    
    app.run(host=host, port=port, debug=debug)