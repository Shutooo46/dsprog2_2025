"""
天気予報アプリケーション用データベース
SQLiteを使用して天気情報を永続化

DB設計:
- areas: エリア情報テーブル（地域コード、地域名）
- forecasts: 天気予報テーブル（今日・明日の予報）
- weekly_forecasts: 週間予報テーブル

正規化:
- 第1正規形: 各カラムは原子値
- 第2正規形: 部分関数従属性を排除
- 第3正規形: 推移的関数従属性を排除（エリア情報を別テーブルに分離）
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "weather.db"


def get_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """データベースを初期化（テーブル作成）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # エリア情報テーブル
    # プライマリーキー: area_code（気象庁の地域コード、一意で不変）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 天気予報テーブル（今日・明日の詳細予報）
    # プライマリーキー: id（自動採番）
    # 複合ユニーク制約: area_code + forecast_date + fetched_at（同じ予報を重複登録しない）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            weather_code TEXT,
            weather_text TEXT,
            temp_min TEXT,
            temp_max TEXT,
            pop TEXT,
            wind TEXT,
            report_datetime TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (area_code) REFERENCES areas(area_code),
            UNIQUE(area_code, forecast_date, fetched_at)
        )
    ''')
    
    # 週間予報テーブル
    # プライマリーキー: id（自動採番）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            weather_code TEXT,
            pop TEXT,
            temp_min TEXT,
            temp_max TEXT,
            reliability TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (area_code) REFERENCES areas(area_code),
            UNIQUE(area_code, forecast_date, fetched_at)
        )
    ''')
    
    # インデックス作成（検索パフォーマンス向上）
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_forecasts_area_date ON forecasts(area_code, forecast_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weekly_area_date ON weekly_forecasts(area_code, forecast_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_forecasts_fetched ON forecasts(fetched_at)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def save_area(area_code: str, area_name: str):
    """エリア情報を保存"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO areas (area_code, area_name, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (area_code, area_name))
    conn.commit()
    conn.close()


def save_areas_batch(areas: list):
    """複数のエリア情報を一括保存"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR REPLACE INTO areas (area_code, area_name, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', areas)
    conn.commit()
    conn.close()


def get_all_areas():
    """全エリア情報を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT area_code, area_name FROM areas ORDER BY area_code')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_forecast(area_code: str, forecast_date: str, weather_code: str,
                  weather_text: str, temp_min: str, temp_max: str,
                  pop: str, wind: str, report_datetime: str):
    """天気予報を保存"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 同じ日の古い予報を削除してから新しい予報を保存
    fetched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO forecasts 
        (area_code, forecast_date, weather_code, weather_text, temp_min, temp_max, pop, wind, report_datetime, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (area_code, forecast_date, weather_code, weather_text, temp_min, temp_max, pop, wind, report_datetime, fetched_at))
    
    conn.commit()
    conn.close()


def save_weekly_forecast(area_code: str, forecast_date: str, weather_code: str,
                         pop: str, temp_min: str, temp_max: str, reliability: str):
    """週間予報を保存"""
    conn = get_connection()
    cursor = conn.cursor()
    
    fetched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO weekly_forecasts
        (area_code, forecast_date, weather_code, pop, temp_min, temp_max, reliability, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (area_code, forecast_date, weather_code, pop, temp_min, temp_max, reliability, fetched_at))
    
    conn.commit()
    conn.close()


def get_latest_forecast(area_code: str, forecast_date: str = None):
    """最新の天気予報を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if forecast_date:
        cursor.execute('''
            SELECT * FROM forecasts 
            WHERE area_code = ? AND forecast_date = ?
            ORDER BY fetched_at DESC
            LIMIT 1
        ''', (area_code, forecast_date))
    else:
        cursor.execute('''
            SELECT * FROM forecasts 
            WHERE area_code = ?
            ORDER BY fetched_at DESC
            LIMIT 2
        ''', (area_code,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_weekly_forecast(area_code: str):
    """最新の週間予報を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 最新のfetched_atを取得
    cursor.execute('''
        SELECT MAX(fetched_at) as latest FROM weekly_forecasts WHERE area_code = ?
    ''', (area_code,))
    result = cursor.fetchone()
    
    if result and result['latest']:
        cursor.execute('''
            SELECT * FROM weekly_forecasts 
            WHERE area_code = ? AND fetched_at = ?
            ORDER BY forecast_date
        ''', (area_code, result['latest']))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    conn.close()
    return []


def get_forecast_history(area_code: str, limit: int = 10):
    """過去の予報履歴を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT fetched_at FROM forecasts 
        WHERE area_code = ?
        ORDER BY fetched_at DESC
        LIMIT ?
    ''', (area_code, limit))
    
    rows = cursor.fetchall()
    conn.close()
    return [row['fetched_at'] for row in rows]


def get_forecast_by_fetched_at(area_code: str, fetched_at: str):
    """特定の取得日時の予報を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM forecasts 
        WHERE area_code = ? AND fetched_at = ?
        ORDER BY forecast_date
    ''', (area_code, fetched_at))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == '__main__':
    init_database()
    print("Database setup complete!")
