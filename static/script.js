// Глобальные переменные
let localStream;
let peerConnection;
const roomId = window.location.pathname.split('/')[2]; // Получаем ID комнаты из URL

// Инициализация при загрузке страницы
window.onload = async () => {
    try {
        // 1. Получаем доступ к камере/микрофону
        localStream = await navigator.mediaDevices.getUserMedia({ 
            video: true, 
            audio: true 
        });
        document.getElementById('localVideo').srcObject = localStream;

        // 2. Настраиваем кнопки
        setupButtons();
        
        // 3. Подключаемся к WebSocket
        setupWebSocket();

    } catch (error) {
        console.error('Ошибка инициализации:', error);
        alert('Не удалось получить доступ к камере/микрофону');
    }
};

// Настройка обработчиков кнопок
function setupButtons() {
    // Кнопка включения/выключения видео
    document.getElementById('toggleVideoBtn').addEventListener('click', () => {
        const videoTrack = localStream.getVideoTracks()[0];
        videoTrack.enabled = !videoTrack.enabled;
        updateButtonStyle('toggleVideoBtn', videoTrack.enabled);
    });

    // Кнопка включения/выключения аудио
    document.getElementById('toggleAudioBtn').addEventListener('click', () => {
        const audioTrack = localStream.getAudioTracks()[0];
        audioTrack.enabled = !audioTrack.enabled;
        updateButtonStyle('toggleAudioBtn', audioTrack.enabled);
    });

    // Кнопка демонстрации экрана
    document.getElementById('screenShareBtn').addEventListener('click', toggleScreenSharing);

    // Кнопка выхода
    document.getElementById('leaveRoomBtn').addEventListener('click', () => {
        window.location.href = '/';
    });
}

// Включение/выключение демонстрации экрана
async function toggleScreenSharing() {
    try {
        const screenStream = await navigator.mediaDevices.getDisplayMedia({ 
            video: { cursor: 'always' },
            audio: false
        });
        
        // Заменяем видео-трек в существующем потоке
        const videoTrack = screenStream.getVideoTracks()[0];
        const sender = peerConnection.getSenders().find(s => s.track.kind === 'video');
        await sender.replaceTrack(videoTrack);
        
        // Обработка завершения демонстрации
        videoTrack.onended = () => {
            const cameraTrack = localStream.getVideoTracks()[0];
            sender.replaceTrack(cameraTrack);
        };
        
    } catch (error) {
        console.error('Ошибка демонстрации экрана:', error);
    }
}

// Настройка WebSocket соединения
function setupWebSocket() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/${roomId}`);

    socket.onopen = () => {
        console.log('WebSocket подключен');
        initializePeerConnection(socket);
    };

    socket.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        
        if (message.type === 'offer') {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(message));
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            socket.send(JSON.stringify(answer));
        }
        // Другие типы сообщений...
    };
}

// Инициализация WebRTC соединения
function initializePeerConnection(socket) {
    peerConnection = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });

    // Добавляем локальный поток
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });

    // Обработка ICE кандидатов
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.send(JSON.stringify({
                type: 'candidate',
                candidate: event.candidate
            }));
        }
    };

    // Получение удаленного потока
    peerConnection.ontrack = (event) => {
        document.getElementById('remoteVideo').srcObject = event.streams[0];
    };
}

// Вспомогательная функция для обновления стиля кнопок
function updateButtonStyle(buttonId, isActive) {
    const button = document.getElementById(buttonId);
    button.style.backgroundColor = isActive ? '#4CAF50' : '#f44336';
    button.innerHTML = isActive ? 
        `${button.textContent} (вкл)` : 
        `${button.textContent} (выкл)`;
}