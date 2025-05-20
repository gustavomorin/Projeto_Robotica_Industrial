// DOM refs
const iniciarBtn      = document.getElementById('iniciarBtn');
const confirmarBtn    = document.getElementById('confirmarBtn');
const snapBtn         = document.getElementById('snapBtn');
const uploadInput     = document.getElementById('uploadInput');
const retakeBtn       = document.getElementById('retakeBtn');
const confirmPhotoBtn = document.getElementById('confirmPhotoBtn');
const video           = document.getElementById('video');
const canvas          = document.getElementById('canvas');
const previewImg      = document.getElementById('previewImg');

const step1         = document.getElementById('step1');
const step2         = document.getElementById('step2');
const step3         = document.getElementById('step3');
const step4         = document.getElementById('step4');
const pointsPreview = document.getElementById('pointsPreview');
const progressFill  = document.getElementById('progressFill');

let photoBlob = null;  // aqui guardamos o Blob da foto

// alerta
function showAlert(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.remove('oculto');
  setTimeout(() => el.classList.add('oculto'), 3000);
}

// STEP1 → STEP2
iniciarBtn.addEventListener('click', () => {
  step1.style.display = 'none';
  step2.style.display = 'block';
});

// STEP2: confirmar altura e posicionar robô
confirmarBtn.addEventListener('click', async () => {
  const altura = parseFloat(document.getElementById('altura').value);
  if (isNaN(altura) || altura <= 0) {
    showAlert('alert-altura', 'Altura inválida');
    return;
  }
  try {
    const res = await fetch('/start_robot', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ height: altura })
    });
    const json = await res.json();
    if (res.ok && json.status === 'posicionado') {
      step2.style.display = 'none';
      step3.style.display = 'block';
      // inicia câmera
      navigator.mediaDevices.getUserMedia({video:true})
        .then(stream => video.srcObject = stream)
        .catch(() => showAlert('alert-photo','Erro ao acessar câmera'));
    } else {
      showAlert('alert-altura', json.message || 'Falha ao posicionar');
    }
  } catch {
    showAlert('alert-altura','Erro de conexão');
  }
});

// STEP3: tirar foto
snapBtn.addEventListener('click', () => {
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(blob => {
    photoBlob = blob;
    previewImg.src = URL.createObjectURL(blob);
    previewImg.style.display = 'block';
    retakeBtn.style.display       = 'inline-block';
    confirmPhotoBtn.style.display = 'inline-block';
    snapBtn.style.display         = 'none';
    uploadInput.style.display     = 'none';
  }, 'image/png');
});

// STEP3: upload de arquivo
uploadInput.addEventListener('change', () => {
  const file = uploadInput.files[0];
  if (!file) return;
  photoBlob = file;
  previewImg.src = URL.createObjectURL(file);
  previewImg.style.display = 'block';
  retakeBtn.style.display       = 'inline-block';
  confirmPhotoBtn.style.display = 'inline-block';
  snapBtn.style.display         = 'none';
  uploadInput.style.display     = 'none';
});

// STEP3: refazer foto/upload
retakeBtn.addEventListener('click', () => {
  photoBlob = null;
  previewImg.style.display      = 'none';
  retakeBtn.style.display       = 'none';
  confirmPhotoBtn.style.display = 'none';
  snapBtn.style.display         = 'inline-block';
  uploadInput.style.display     = 'inline-block';
});

// STEP3 → STEP4: confirmar e processar
confirmPhotoBtn.addEventListener('click', async () => {
  if (!photoBlob) {
    showAlert('alert-photo','Nenhuma foto para enviar');
    return;
  }
  // upload da foto ou arquivo
  const fd = new FormData();
  fd.append('image', photoBlob, 'foto.png');
  const up = await fetch('/capture_photo',{method:'POST',body:fd}).then(r=>r.json());
  if (up.status !== 'received') {
    showAlert('alert-photo','Erro ao enviar foto');
    return;
  }

  // processamento
  const pr = await fetch('/process_photo',{method:'POST'}).then(r=>r.json());
  if (pr.status === 'done') {
    // vai para STEP4
    step3.style.display = 'none';
    step4.style.display = 'block';
    // preview da imagem de pontos
    pointsPreview.src = '/img/pontos_dither_debug.png';
    // simula progresso (ajuste totalChunks conforme real)
    const totalChunks = 10;
    for (let i=1; i<=totalChunks; i++) {
      await new Promise(r=>setTimeout(r,200));
      progressFill.style.width = `${Math.round((i/totalChunks)*100)}%`;
    }
  } else {
    showAlert('alert-photo','Erro no processamento');
  }
});
