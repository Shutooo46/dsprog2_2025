"""
天気予報アプリケーション用APIサーバー
Flask + SQLiteでバックエンドを構築
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime
import database as db

app = Flask(__name__)
CORS(app)  # フロントエンドからのアクセスを許可

# 気象庁API
JMA_AREA_URL = 'https://www.jma.go.jp/bosai/common/const/area.json'
JMA_FORECAST_URL = 'https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json'


@app.route('/api/areas', methods=['GET'])
def get_areas():
    """エリア一覧を取得（DBから、なければAPIから取得してDBに保存）"""
    areas = db.get_all_areas()
    
    if not areas:
        # DBにデータがない場合、APIから取得して保存
        try:
            response = requests.get(JMA_AREA_URL)
            response.raise_for_status()
            data = response.json()
            
            offices = data.get('offices', {})
            area_list = [(code, info['name']) for code, info in offices.items()]
            db.save_areas_batch(area_list)
            
            areas = db.get_all_areas()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify(areas)


@app.route('/api/areas/refresh', methods=['POST'])
def refresh_areas():
    """エリア情報をAPIから再取得してDBを更新"""
    try:
        response = requests.get(JMA_AREA_URL)
        response.raise_for_status()
        data = response.json()
        
        offices = data.get('offices', {})
        area_list = [(code, info['name']) for code, info in offices.items()]
        db.save_areas_batch(area_list)
        
        return jsonify({'message': 'Areas refreshed', 'count': len(area_list)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forecast/<area_code>', methods=['GET'])
def get_forecast(area_code):
    """天気予報を取得（APIから取得してDBに保存し、DBから返す）"""
    try:
        # 気象庁APIから最新データを取得
        response = requests.get(JMA_FORECAST_URL.format(area_code))
        response.raise_for_status()
        data = response.json()
        
        # データを解析してDBに保存
        forecast_data = parse_and_save_forecast(area_code, data)
        
        return jsonify(forecast_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forecast/<area_code>/latest', methods=['GET'])
def get_latest_forecast(area_code):
    """DBから最新の予報を取得"""
    forecasts = db.get_latest_forecast(area_code)
    weekly = db.get_latest_weekly_forecast(area_code)
    
    return jsonify({
        'forecasts': forecasts,
        'weekly': weekly
    })


@app.route('/api/forecast/<area_code>/history', methods=['GET'])
def get_forecast_history(area_code):
    """過去の予報履歴を取得"""
    limit = request.args.get('limit', 10, type=int)
    history = db.get_forecast_history(area_code, limit)
    return jsonify(history)


@app.route('/api/forecast/<area_code>/history/<fetched_at>', methods=['GET'])
def get_historical_forecast(area_code, fetched_at):
    """特定の日時の予報を取得"""
    forecasts = db.get_forecast_by_fetched_at(area_code, fetched_at)
    return jsonify(forecasts)


def parse_and_save_forecast(area_code: str, data: list) -> dict:
    """気象庁APIのレスポンスを解析してDBに保存"""
    result = {
        'today': None,
        'tomorrow': None,
        'weekly': [],
        'report_datetime': None,
        'area_name': None
    }
    
    if len(data) < 1:
        return result
    
    forecast = data[0]
    result['report_datetime'] = forecast.get('reportDatetime', '')
    
    # 今日・明日の予報を解析
    time_series = forecast.get('timeSeries', [])
    if len(time_series) >= 1:
        weather_ts = time_series[0]
        time_defines = weather_ts.get('timeDefines', [])
        areas = weather_ts.get('areas', [])
        
        if areas:
            area = areas[0]
            result['area_name'] = area.get('area', {}).get('name', '')
            weather_codes = area.get('weatherCodes', [])
            weathers = area.get('weathers', [])
            winds = area.get('winds', [])
            
            # 降水確率
            pops = []
            if len(time_series) > 1:
                pop_areas = time_series[1].get('areas', [])
                if pop_areas:
                    pops = pop_areas[0].get('pops', [])
            
            # 気温
            temps = []
            if len(time_series) > 2:
                temp_areas = time_series[2].get('areas', [])
                if temp_areas:
                    temps = temp_areas[0].get('temps', [])
            
            # 今日の予報
            if len(time_defines) > 0:
                today_date = time_defines[0][:10]
                today_weather_code = weather_codes[0] if weather_codes else ''
                today_weather_text = weathers[0] if weathers else ''
                today_wind = winds[0] if winds else ''
                today_pop = max([int(p) for p in pops[:4] if p], default=0) if pops else ''
                today_temp_min = temps[0] if len(temps) > 0 else ''
                today_temp_max = temps[1] if len(temps) > 1 else ''
                
                db.save_forecast(
                    area_code, today_date, today_weather_code, today_weather_text,
                    str(today_temp_min), str(today_temp_max), str(today_pop),
                    today_wind, result['report_datetime']
                )
                
                result['today'] = {
                    'date': today_date,
                    'weather_code': today_weather_code,
                    'weather_text': today_weather_text,
                    'temp_min': today_temp_min,
                    'temp_max': today_temp_max,
                    'pop': today_pop,
                    'wind': today_wind
                }
            
            # 明日の予報
            if len(time_defines) > 1:
                tomorrow_date = time_defines[1][:10]
                tomorrow_weather_code = weather_codes[1] if len(weather_codes) > 1 else ''
                tomorrow_weather_text = weathers[1] if len(weathers) > 1 else ''
                tomorrow_wind = winds[1] if len(winds) > 1 else ''
                tomorrow_pop = max([int(p) for p in pops[4:8] if p], default=0) if len(pops) > 4 else ''
                
                result['tomorrow'] = {
                    'date': tomorrow_date,
                    'weather_code': tomorrow_weather_code,
                    'weather_text': tomorrow_weather_text,
                    'pop': tomorrow_pop,
                    'wind': tomorrow_wind
                }
    
    # 週間予報を解析
    if len(data) > 1:
        weekly_data = data[1]
        weekly_ts = weekly_data.get('timeSeries', [])
        
        if weekly_ts:
            time_defines = weekly_ts[0].get('timeDefines', [])
            areas = weekly_ts[0].get('areas', [])
            
            if areas:
                area = areas[0]
                weather_codes = area.get('weatherCodes', [])
                pops = area.get('pops', [])
                reliabilities = area.get('reliabilities', [])
                
                # 気温データ
                temp_mins = []
                temp_maxs = []
                if len(weekly_ts) > 1:
                    temp_areas = weekly_ts[1].get('areas', [])
                    if temp_areas:
                        temp_mins = temp_areas[0].get('tempsMin', [])
                        temp_maxs = temp_areas[0].get('tempsMax', [])
                
                for i, date in enumerate(time_defines):
                    forecast_date = date[:10]
                    weather_code = weather_codes[i] if i < len(weather_codes) else ''
                    pop = pops[i] if i < len(pops) else ''
                    reliability = reliabilities[i] if i < len(reliabilities) else ''
                    temp_min = temp_mins[i] if i < len(temp_mins) else ''
                    temp_max = temp_maxs[i] if i < len(temp_maxs) else ''
                    
                    db.save_weekly_forecast(
                        area_code, forecast_date, weather_code,
                        str(pop), str(temp_min), str(temp_max), reliability
                    )
                    
                    result['weekly'].append({
                        'date': forecast_date,
                        'weather_code': weather_code,
                        'pop': pop,
                        'temp_min': temp_min,
                        'temp_max': temp_max,
                        'reliability': reliability
                    })
    
    return result


if __name__ == '__main__':
    # データベース初期化
    db.init_database()
    
    # サーバー起動
    print("Starting Weather API Server...")
    app.run(debug=True, port=5000)
