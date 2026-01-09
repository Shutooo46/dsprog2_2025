// ===== Configuration =====
const API_BASE_URL = 'http://localhost:5001/api';

const API_ENDPOINTS = {
    areas: `${API_BASE_URL}/areas`,
    forecast: (areaCode) => `${API_BASE_URL}/forecast/${areaCode}`,
    latestForecast: (areaCode) => `${API_BASE_URL}/forecast/${areaCode}/latest`,
    forecastHistory: (areaCode) => `${API_BASE_URL}/forecast/${areaCode}/history`,
    historicalForecast: (areaCode, fetchedAt) => `${API_BASE_URL}/forecast/${areaCode}/history/${encodeURIComponent(fetchedAt)}`
};

// ===== Weather Code to Emoji Mapping =====
const WEATHER_ICONS = {
    '100': '☀️', '101': '🌤️', '102': '🌤️', '103': '🌤️', '104': '🌤️',
    '110': '🌤️', '111': '🌤️', '112': '🌤️', '113': '🌤️', '114': '🌤️',
    '115': '🌤️', '116': '🌤️', '117': '🌤️', '118': '🌤️',
    '119': '🌤️', '120': '🌤️', '121': '🌤️', '122': '🌤️', '123': '🌤️',
    '124': '🌤️', '125': '🌤️', '126': '🌤️', '127': '🌤️', '128': '🌤️',
    '130': '🌤️', '131': '🌤️', '132': '🌤️', '140': '🌤️', '160': '🌤️',
    '170': '🌤️',
    '200': '☁️', '201': '☁️', '202': '☁️', '203': '☁️', '204': '☁️',
    '205': '☁️', '206': '☁️', '207': '☁️', '208': '☁️', '209': '☁️',
    '210': '☁️', '211': '☁️', '212': '☁️', '213': '☁️', '214': '☁️',
    '215': '☁️', '216': '☁️', '217': '☁️', '218': '☁️', '219': '☁️',
    '220': '☁️', '221': '☁️', '222': '☁️', '223': '☁️', '224': '☁️',
    '225': '☁️', '226': '☁️', '228': '☁️', '229': '☁️', '230': '☁️',
    '231': '☁️', '240': '☁️', '250': '☁️', '260': '☁️', '270': '☁️',
    '281': '☁️',
    '300': '🌧️', '301': '🌧️', '302': '🌧️', '303': '🌧️', '304': '🌧️',
    '306': '🌧️', '308': '🌧️', '309': '🌧️', '311': '🌧️', '313': '🌧️',
    '314': '🌧️', '315': '🌧️', '316': '🌧️', '317': '🌧️', '320': '🌧️',
    '321': '🌧️', '322': '🌧️', '323': '🌧️', '324': '🌧️', '325': '🌧️',
    '326': '🌧️', '327': '🌧️', '328': '🌧️', '329': '🌧️', '340': '🌧️',
    '350': '🌧️',
    '400': '❄️', '401': '❄️', '402': '❄️', '403': '❄️', '405': '❄️',
    '406': '❄️', '407': '❄️', '409': '❄️', '411': '❄️', '413': '❄️',
    '414': '❄️', '420': '❄️', '421': '❄️', '422': '❄️', '423': '❄️',
    '425': '❄️', '426': '❄️', '427': '❄️', '430': '❄️', '450': '❄️'
};

// ===== DOM Elements =====
const elements = {
    areaSelect: document.getElementById('area-select'),
    historySelect: document.getElementById('history-select'),
    loading: document.getElementById('loading'),
    weatherDisplay: document.getElementById('weather-display'),
    errorMessage: document.getElementById('error-message'),
    errorText: document.getElementById('error-text'),
    areaName: document.getElementById('area-name'),
    updateTime: document.getElementById('update-time'),
    dataSource: document.getElementById('data-source'),
    todayIcon: document.getElementById('today-icon'),
    todayWeatherText: document.getElementById('today-weather-text'),
    todayTemp: document.getElementById('today-temp'),
    todayPop: document.getElementById('today-pop'),
    todayWind: document.getElementById('today-wind'),
    tomorrowIcon: document.getElementById('tomorrow-icon'),
    tomorrowWeatherText: document.getElementById('tomorrow-weather-text'),
    tomorrowTemp: document.getElementById('tomorrow-temp'),
    tomorrowPop: document.getElementById('tomorrow-pop'),
    tomorrowWind: document.getElementById('tomorrow-wind'),
    weeklyList: document.getElementById('weekly-list')
};

// ===== State =====
let currentAreaCode = null;

// ===== Utility Functions =====
function getWeatherIcon(code) {
    return WEATHER_ICONS[code] || '🌈';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')} 更新`;
}

function formatHistoryDate(dateString) {
    const date = new Date(dateString);
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
}

function getDayName(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
        return '今日';
    }
    if (date.toDateString() === tomorrow.toDateString()) {
        return '明日';
    }
    
    const dayNames = ['日', '月', '火', '水', '木', '金', '土'];
    return `${date.getMonth() + 1}/${date.getDate()}(${dayNames[date.getDay()]})`;
}

function showElement(element) {
    if (element) element.style.display = '';
}

function hideElement(element) {
    if (element) element.style.display = 'none';
}

function showLoading() {
    showElement(elements.loading);
    hideElement(elements.weatherDisplay);
    hideElement(elements.errorMessage);
}

function hideLoading() {
    hideElement(elements.loading);
}

function showError(message) {
    hideLoading();
    elements.errorText.textContent = message;
    showElement(elements.errorMessage);
    hideElement(elements.weatherDisplay);
}

// ===== API Functions =====
async function fetchAreas() {
    try {
        const response = await fetch(API_ENDPOINTS.areas);
        if (!response.ok) throw new Error('エリアリストの取得に失敗しました');
        return await response.json();
    } catch (error) {
        console.error('Error fetching areas:', error);
        throw error;
    }
}

async function fetchForecast(areaCode) {
    try {
        const response = await fetch(API_ENDPOINTS.forecast(areaCode));
        if (!response.ok) throw new Error('天気予報の取得に失敗しました');
        return await response.json();
    } catch (error) {
        console.error('Error fetching forecast:', error);
        throw error;
    }
}

async function fetchForecastHistory(areaCode) {
    try {
        const response = await fetch(API_ENDPOINTS.forecastHistory(areaCode));
        if (!response.ok) throw new Error('履歴の取得に失敗しました');
        return await response.json();
    } catch (error) {
        console.error('Error fetching history:', error);
        throw error;
    }
}

async function fetchHistoricalForecast(areaCode, fetchedAt) {
    try {
        const response = await fetch(API_ENDPOINTS.historicalForecast(areaCode, fetchedAt));
        if (!response.ok) throw new Error('過去の予報の取得に失敗しました');
        return await response.json();
    } catch (error) {
        console.error('Error fetching historical forecast:', error);
        throw error;
    }
}

// ===== UI Functions =====
function populateAreaDropdown(areas) {
    elements.areaSelect.innerHTML = '<option value="">地域を選択してください</option>';
    
    areas.sort((a, b) => a.area_code.localeCompare(b.area_code));
    
    areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area.area_code;
        option.textContent = area.area_name;
        elements.areaSelect.appendChild(option);
    });
}

async function populateHistoryDropdown(areaCode) {
    if (!elements.historySelect) return;
    
    try {
        const history = await fetchForecastHistory(areaCode);
        elements.historySelect.innerHTML = '<option value="">最新の予報</option>';
        
        history.forEach(fetchedAt => {
            const option = document.createElement('option');
            option.value = fetchedAt;
            option.textContent = formatHistoryDate(fetchedAt);
            elements.historySelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayForecast(data, areaName, fromDB = false) {
    hideLoading();
    hideElement(elements.errorMessage);
    
    elements.areaName.textContent = areaName;
    elements.updateTime.textContent = formatDate(data.report_datetime || new Date().toISOString());
    
    if (elements.dataSource) {
        elements.dataSource.textContent = fromDB ? '📁 DBから取得' : '🌐 APIから取得';
    }
    
    // 今日の天気
    if (data.today) {
        elements.todayIcon.textContent = getWeatherIcon(data.today.weather_code);
        elements.todayWeatherText.textContent = data.today.weather_text || '情報なし';
        elements.todayWind.textContent = data.today.wind || '-';
        
        const tempMin = data.today.temp_min || '-';
        const tempMax = data.today.temp_max || '-';
        elements.todayTemp.textContent = `${tempMin}°C / ${tempMax}°C`;
        elements.todayPop.textContent = data.today.pop ? `${data.today.pop}%` : '-';
    }
    
    // 明日の天気
    if (data.tomorrow) {
        elements.tomorrowIcon.textContent = getWeatherIcon(data.tomorrow.weather_code);
        elements.tomorrowWeatherText.textContent = data.tomorrow.weather_text || '情報なし';
        elements.tomorrowWind.textContent = data.tomorrow.wind || '-';
        elements.tomorrowPop.textContent = data.tomorrow.pop ? `${data.tomorrow.pop}%` : '-';
        elements.tomorrowTemp.textContent = '-';
    }
    
    // 週間予報
    displayWeeklyForecast(data.weekly || []);
    
    showElement(elements.weatherDisplay);
}

function displayWeeklyForecast(weeklyData) {
    elements.weeklyList.innerHTML = '';
    
    if (!weeklyData || weeklyData.length === 0) {
        elements.weeklyList.innerHTML = '<p class="no-data">週間予報データがありません</p>';
        return;
    }
    
    // 最初の1日（今日）をスキップして表示
    weeklyData.slice(1, 7).forEach(day => {
        const item = document.createElement('div');
        item.className = 'weekly-item';
        
        const dayName = getDayName(day.date);
        const icon = getWeatherIcon(day.weather_code);
        const pop = day.pop;
        
        item.innerHTML = `
            <span class="weekly-day">${dayName}</span>
            <span class="weekly-icon">${icon}</span>
            <span class="weekly-weather"></span>
            <span class="weekly-pop">${pop !== undefined && pop !== '' ? pop + '%' : '-'}</span>
        `;
        
        elements.weeklyList.appendChild(item);
    });
}

// ===== Event Handlers =====
async function handleAreaChange(event) {
    const areaCode = event.target.value;
    currentAreaCode = areaCode;
    
    if (!areaCode) {
        hideElement(elements.weatherDisplay);
        hideElement(elements.errorMessage);
        return;
    }
    
    showLoading();
    
    try {
        const forecast = await fetchForecast(areaCode);
        const selectedOption = elements.areaSelect.options[elements.areaSelect.selectedIndex];
        displayForecast(forecast, selectedOption.textContent, false);
        
        // 履歴を読み込む
        await populateHistoryDropdown(areaCode);
    } catch (error) {
        showError('天気予報の取得に失敗しました。サーバーが起動しているか確認してください。');
    }
}

async function handleHistoryChange(event) {
    const fetchedAt = event.target.value;
    
    if (!fetchedAt || !currentAreaCode) {
        // 最新の予報を再取得
        if (currentAreaCode) {
            const forecast = await fetchForecast(currentAreaCode);
            const selectedOption = elements.areaSelect.options[elements.areaSelect.selectedIndex];
            displayForecast(forecast, selectedOption.textContent, false);
        }
        return;
    }
    
    showLoading();
    
    try {
        const forecasts = await fetchHistoricalForecast(currentAreaCode, fetchedAt);
        const selectedOption = elements.areaSelect.options[elements.areaSelect.selectedIndex];
        
        // 過去の予報データを整形
        const data = {
            today: forecasts[0] || null,
            tomorrow: forecasts[1] || null,
            weekly: [],
            report_datetime: forecasts[0]?.report_datetime || fetchedAt
        };
        
        displayForecast(data, selectedOption.textContent, true);
    } catch (error) {
        showError('過去の予報の取得に失敗しました。');
    }
}

// ===== Initialization =====
async function init() {
    try {
        const areas = await fetchAreas();
        populateAreaDropdown(areas);
        
        elements.areaSelect.addEventListener('change', handleAreaChange);
        
        if (elements.historySelect) {
            elements.historySelect.addEventListener('change', handleHistoryChange);
        }
    } catch (error) {
        showError('エリアリストの取得に失敗しました。サーバーが起動しているか確認してください。');
    }
}

// Start the app
document.addEventListener('DOMContentLoaded', init);
