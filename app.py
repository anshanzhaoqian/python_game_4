import random
from flask import Flask, render_template, jsonify, request, session

app = Flask(__name__)
app.secret_key = 'shitoujiandaobu_secret_key_2024'

# 游戏选项
CHOICES = {
    'rock': '石头 ✊',
    'scissors': '剪刀 ✌️',
    'paper': '布 ✋'
}

# 胜负规则：key 胜 value
RULES = {
    'rock': 'scissors',      # 石头胜剪刀
    'scissors': 'paper',     # 剪刀胜布
    'paper': 'rock'          # 布胜石头
}


def init_session():
    """初始化 session 中的游戏数据"""
    if 'stats' not in session:
        session['stats'] = {
            'total': 0,      # 总局数
            'win': 0,        # 胜利局数
            'lose': 0,       # 失败局数
            'draw': 0,       # 平局局数
            'history': []    # 历史记录
        }


def determine_winner(player_choice, computer_choice):
    """判断胜负
    返回: 'win', 'lose', 'draw'
    """
    if player_choice == computer_choice:
        return 'draw'
    if RULES[player_choice] == computer_choice:
        return 'win'
    return 'lose'


def get_win_rate(stats):
    """计算胜率"""
    if stats['total'] == 0:
        return 0.0
    return round(stats['win'] / stats['total'] * 100, 1)


@app.route('/')
def index():
    """主页面"""
    init_session()
    return render_template('index.html')


@app.route('/api/play', methods=['POST'])
def play():
    """处理一局游戏"""
    init_session()
    data = request.get_json()
    player_choice = data.get('choice', '')

    if player_choice not in CHOICES:
        return jsonify({'error': '无效的选择'}), 400

    # 电脑随机选择
    computer_choice = random.choice(list(CHOICES.keys()))

    # 判断胜负
    result = determine_winner(player_choice, computer_choice)

    # 更新统计数据
    stats = session['stats']
    stats['total'] += 1
    if result == 'win':
        stats['win'] += 1
    elif result == 'lose':
        stats['lose'] += 1
    else:
        stats['draw'] += 1

    # 记录历史（保留最近20条）
    stats['history'].append({
        'round': stats['total'],
        'player': player_choice,
        'computer': computer_choice,
        'result': result
    })
    if len(stats['history']) > 20:
        stats['history'] = stats['history'][-20:]

    session['stats'] = stats

    win_rate = get_win_rate(stats)

    return jsonify({
        'player_choice': player_choice,
        'player_choice_cn': CHOICES[player_choice],
        'computer_choice': computer_choice,
        'computer_choice_cn': CHOICES[computer_choice],
        'result': result,
        'stats': {
            'total': stats['total'],
            'win': stats['win'],
            'lose': stats['lose'],
            'draw': stats['draw'],
            'win_rate': win_rate
        },
        'history': stats['history']
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    """重置游戏数据"""
    session['stats'] = {
        'total': 0,
        'win': 0,
        'lose': 0,
        'draw': 0,
        'history': []
    }
    return jsonify({'message': '数据已重置', 'stats': session['stats']})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取当前统计数据"""
    init_session()
    stats = session['stats']
    stats['win_rate'] = get_win_rate(stats)
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
