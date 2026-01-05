// ===== Configuration =====
const API_ENDPOINTS = {
    areaList: 'https://www.jma.go.jp/bosai/common/const/area.json',
    forecast: (areaCode) => `https://www.jma.go.jp/bosai/forecast/data/forecast/${areaCode}.json`
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
    loading: document.getElementById('loading'),
    weatherDisplay: document.getElementById('weather-display'),
    errorMessage: document.getElementById('error-message'),
    errorText: document.getElementById('error-text'),
    areaName: document.getElementById('area-name'),
    updateTime: document.getElementById('update-time'),
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

// ===== Utility Functions =====
function getWeatherIcon(code) {
    return WEATHER_ICONS[code] || '🌈';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')} 更新`;
}

function getDayName(dateString, isToday = false) {
    if (isToday) return '今日';
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === tomorrow.toDateString()) {
        return '明日';
    }
    
    const dayNames = ['日', '月', '火', '水', '木', '金', '土'];
    return `${date.getMonth() + 1}/${date.getDate()}(${dayNames[date.getDay()]})`;
}

function showElement(element) {
    element.style.display = '';
}

function hideElement(element) {
    element.style.display = 'none';
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
async function fetchAreaList() {
    try {
        const response = await fetch(API_ENDPOINTS.areaList);
        if (!response.ok) throw new Error('地域リストの取得に失敗しました');
        return await response.json();
    } catch (error) {
        console.error('Error fetching area list:', error);
        throw error;
    }
}

async function fetchWeatherForecast(areaCode) {
    try {
        const response = await fetch(API_ENDPOINTS.forecast(areaCode));
        if (!response.ok) throw new Error('天気予報の取得に失敗しました');
        return await response.json();
    } catch (error) {
        console.error('Error fetching weather forecast:', error);
        throw error;
    }
}

// ===== UI Functions =====
function populateAreaDropdown(areaData) {
    const offices = areaData.offices;
    
    // Sort by area code
    const sortedOffices = Object.entries(offices).sort((a, b) => {
        return a[0].localeCompare(b[0]);
    });
    
    // Clear existing options except the first one
    elements.areaSelect.innerHTML = '<option value="">地域を選択してください</option>';
    
    // Add options
    sortedOffices.forEach(([code, data]) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = data.name;
        elements.areaSelect.appendChild(option);
    });
}

function displayWeatherForecast(data, areaName) {
    hideLoading();
    hideElement(elements.errorMessage);
    
    // Get forecast data
    const forecast = data[0];
    const weeklyData = data[1];
    
    // Set area name and update time
    elements.areaName.textContent = areaName;
    elements.updateTime.textContent = formatDate(forecast.reportDatetime);
    
    // Get first area's data (main area)
    const areas = forecast.timeSeries[0].areas;
    const pops = forecast.timeSeries[1]?.areas || [];
    const temps = forecast.timeSeries[2]?.areas || [];
    
    if (areas.length > 0) {
        const todayArea = areas[0];
        
        // Today's weather
        elements.todayIcon.textContent = getWeatherIcon(todayArea.weatherCodes[0]);
        elements.todayWeatherText.textContent = todayArea.weathers?.[0] || '情報なし';
        elements.todayWind.textContent = todayArea.winds?.[0] || '-';
        
        // Today's temperature
        if (temps.length > 0) {
            const tempData = temps[0];
            const minTemp = tempData.temps?.[0] || '-';
            const maxTemp = tempData.temps?.[1] || '-';
            elements.todayTemp.textContent = `${minTemp}°C / ${maxTemp}°C`;
        } else {
            elements.todayTemp.textContent = '-';
        }
        
        // Today's precipitation probability
        if (pops.length > 0) {
            const popValues = pops[0].pops || [];
            const maxPop = Math.max(...popValues.filter(p => p !== '').map(Number));
            elements.todayPop.textContent = `${maxPop}%`;
        } else {
            elements.todayPop.textContent = '-';
        }
        
        // Tomorrow's weather
        if (todayArea.weatherCodes.length > 1) {
            elements.tomorrowIcon.textContent = getWeatherIcon(todayArea.weatherCodes[1]);
            elements.tomorrowWeatherText.textContent = todayArea.weathers?.[1] || '情報なし';
            elements.tomorrowWind.textContent = todayArea.winds?.[1] || '-';
        }
        
        // Tomorrow's temperature from weekly data
        if (weeklyData && weeklyData.timeSeries && weeklyData.timeSeries[1]) {
            const weeklyTemps = weeklyData.timeSeries[1].areas[0];
            if (weeklyTemps) {
                const minTemp = weeklyTemps.tempsMin?.[1] || '-';
                const maxTemp = weeklyTemps.tempsMax?.[1] || '-';
                elements.tomorrowTemp.textContent = `${minTemp}°C / ${maxTemp}°C`;
            }
        } else {
            elements.tomorrowTemp.textContent = '-';
        }
        
        // Tomorrow's precipitation probability
        if (pops.length > 0 && pops[0].pops) {
            const popValues = pops[0].pops;
            const tomorrowPops = popValues.slice(4, 8).filter(p => p !== '').map(Number);
            if (tomorrowPops.length > 0) {
                const maxPop = Math.max(...tomorrowPops);
                elements.tomorrowPop.textContent = `${maxPop}%`;
            } else {
                elements.tomorrowPop.textContent = '-';
            }
        } else {
            elements.tomorrowPop.textContent = '-';
        }
    }
    
    // Weekly forecast
    displayWeeklyForecast(weeklyData);
    
    showElement(elements.weatherDisplay);
}

function displayWeeklyForecast(weeklyData) {
    elements.weeklyList.innerHTML = '';
    
    if (!weeklyData || !weeklyData.timeSeries) {
        elements.weeklyList.innerHTML = '<p class="no-data">週間予報データがありません</p>';
        return;
    }
    
    const timeSeries = weeklyData.timeSeries[0];
    const timeDefines = timeSeries.timeDefines;
    const areas = timeSeries.areas[0];
    
    // Skip first item (today) and show next 6 days
    for (let i = 1; i < Math.min(timeDefines.length, 7); i++) {
        const item = document.createElement('div');
        item.className = 'weekly-item';
        
        const dayName = getDayName(timeDefines[i]);
        const icon = getWeatherIcon(areas.weatherCodes[i]);
        const pop = areas.pops?.[i];
        
        item.innerHTML = `
            <span class="weekly-day">${dayName}</span>
            <span class="weekly-icon">${icon}</span>
            <span class="weekly-weather"></span>
            <span class="weekly-pop">${pop !== undefined && pop !== '' ? pop + '%' : '-'}</span>
        `;
        
        elements.weeklyList.appendChild(item);
    }
}

// ===== Event Handlers =====
async function handleAreaChange(event) {
    const areaCode = event.target.value;
    
    if (!areaCode) {
        hideElement(elements.weatherDisplay);
        hideElement(elements.errorMessage);
        return;
    }
    
    showLoading();
    
    try {
        const forecast = await fetchWeatherForecast(areaCode);
        const selectedOption = elements.areaSelect.options[elements.areaSelect.selectedIndex];
        displayWeatherForecast(forecast, selectedOption.textContent);
    } catch (error) {
        showError('天気予報の取得に失敗しました。しばらくしてからもう一度お試しください。');
    }
}

// ===== Initialization =====
async function init() {
    try {
        const areaData = await fetchAreaList();
        populateAreaDropdown(areaData);
        
        // Add event listener
        elements.areaSelect.addEventListener('change', handleAreaChange);
    } catch (error) {
        showError('地域リストの取得に失敗しました。ページを再読み込みしてください。');
    }
}

// Start the app
document.addEventListener('DOMContentLoaded', init);
