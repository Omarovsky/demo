// Создание комнаты
async function createRoom() {
    const response = await fetch("/create_room");
    const { room_id } = await response.json();
    window.location.href = `/room/${room_id}`;
}

// Подключение к WebRTC в комнате
async function startScreenSharing() {
    const pc = new RTCPeerConnection({ iceServers: [{ urls: "stun:stun.l.google.com:19302" }] });
    const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
    document.getElementById("remoteVideo").srcObject = stream;
    
    // Отправка ICE-кандидатов через WebSocket
    pc.onicecandidate = (event) => {
        if (event.candidate) {
            ws.send(JSON.stringify({ type: "ice", candidate: event.candidate }));
        }
    };
}




const roomId = '{{ room_id }}';
const roomLink = `${window.location.origin}/room/${roomId}`;

// Элементы интерфейса
const localVideo = document.getElementById('localVideo');
const videoGrid = document.getElementById('videoGrid');
const copyLinkBtn = document.getElementById('copyLinkBtn');
const toggleVideoBtn = document.getElementById('toggleVideoBtn');
const toggleAudioBtn = document.getElementById('toggleAudioBtn');
const screenShareBtn = document.getElementById('screenShareBtn');
const leaveRoomBtn = document.getElementById('leaveRoomBtn');
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendMessageBtn = document.getElementById('sendMessageBtn');

// Состояние медиа
let localStrea;
let isVideoOn = true;
let isAudioOn = true;
let isScreenSharing = false;
let peerConnections = {};

// Инициализация WebSocket соединения
const ws = new WebSocket(`ws://${window.location.host}/ws/${roomId}`);

// Копирование ссылки на комнату
copyLinkBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(roomLink)
        .then(() => alert('Ссылка скопирована!'))
        .catch(err => console.error('Ошибка копирования:', err));
});

// Выход из комнаты
leaveRoomBtn.addEventListener('click', () => {
    window.location.href = '/';
});

// Отправка сообщения
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        ws.send(JSON.stringify({
            type: 'chat',
            message: message
        }));
        messageInput.value = '';
    }
}

sendMessageBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

console.log('Подключение к комнате:', roomId);

// Инициализация потоков
let localStream;

async function init() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        document.getElementById('localVideo').srcObject = localStream;
        setupButtons();
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Настройка кнопок
function setupButtons() {
    document.getElementById('toggleVideoBtn').addEventListener('click', () => {
        const track = localStream.getVideoTracks()[0];
        track.enabled = !track.enabled;
    });

    document.getElementById('toggleAudioBtn').addEventListener('click', () => {
        const track = localStream.getAudioTracks()[0];
        track.enabled = !track.enabled;
    });

    document.getElementById('screenShareBtn').addEventListener('click', async () => {
        const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        document.getElementById('remoteVideo').srcObject = stream;
    });
}

// Запуск при загрузке
window.onload = init;