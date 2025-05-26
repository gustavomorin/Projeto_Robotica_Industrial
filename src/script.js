const iniciarBtn      = document.getElementById('iniciarBtn');
const confirmarBtn    = document.getElementById('confirmarBtn');
const snapBtn         = document.getElementById('snapBtn');
const uploadInput     = document.getElementById('uploadInput');
const retakeBtn       = document.getElementById('retakeBtn');
const testPhotoBtn    = document.getElementById('testPhotoBtn');
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

let photoBlob = null;

function showAlert(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.remove('oculto');
  setTimeout(() => el.classList.add('oculto'), 3000);
}

iniciarBtn.addEventListener('click', () => {
  step1.style.display = 'none';
  step2.style.display = 'block';
});

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

snapBtn.addEventListener('click', () => {
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(blob => {
    photoBlob = blob;
    previewImg.src = URL.createObjectURL(blob);
    previewImg.style.display = 'block';
    retakeBtn.style.display       = 'inline-block';
    testPhotoBtn.style.display    = 'inline-block';
    confirmPhotoBtn.style.display = 'inline-block';
    snapBtn.style.display         = 'none';
    uploadInput.style.display     = 'none';
  }, 'image/png');
});

uploadInput.addEventListener('change', () => {
  const file = uploadInput.files[0];
  if (!file) return;
  photoBlob = file;
  previewImg.src = URL.createObjectURL(file);
  previewImg.style.display = 'block';
  retakeBtn.style.display       = 'inline-block';
  testPhotoBtn.style.display    = 'inline-block';
  confirmPhotoBtn.style.display = 'inline-block';
  snapBtn.style.display         = 'none';
  uploadInput.style.display     = 'none';
});

retakeBtn.addEventListener('click', () => {
  photoBlob = null;
  previewImg.style.display      = 'none';
  retakeBtn.style.display       = 'none';
  testPhotoBtn.style.display    = 'none';
  confirmPhotoBtn.style.display = 'none';
  snapBtn.style.display         = 'inline-block';
  uploadInput.style.display     = 'inline-block';
});

testPhotoBtn.addEventListener('click', async () => {
  if (!photoBlob) {
    showAlert('alert-photo','Nenhuma foto para testar');
    return;
  }

  const fd = new FormData();
  fd.append('image', photoBlob, 'foto.png');

  const formatoFolha = document.getElementById('formato').value;
  const largura = parseInt(document.getElementById('largura').value);
  const altura_res = parseInt(document.getElementById('altura_res').value);

  const up = await fetch('/capture_photo',{method:'POST',body:fd}).then(r=>r.json());
  if (up.status !== 'received') {
    showAlert('alert-photo','Erro ao enviar foto');
    return;
  }

  const pr = await fetch('/test_photo', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      formato: formatoFolha,
      largura: largura,
      altura: altura_res
    })
  }).then(r=>r.json());

  if (pr.status === 'tested') {
    showAlert('alert-photo','Foto processada para teste. Veja o preview!');
    pointsPreview.src = '/img/pontos_dither_debug.png';
    step4.style.display = 'block';
  } else {
    showAlert('alert-photo','Erro no processamento');
  }
});

confirmPhotoBtn.addEventListener('click', async () => {
  if (!photoBlob) {
    showAlert('alert-photo','Nenhuma foto para confirmar');
    return;
  }

  const formatoFolha = document.getElementById('formato').value;
  const largura = parseInt(document.getElementById('largura').value);
  const altura_res = parseInt(document.getElementById('altura_res').value);

  const pr = await fetch('/process_photo', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      formato: formatoFolha,
      largura: largura,
      altura: altura_res
    })
  }).then(r=>r.json());

  if (pr.status === 'done') {
    step3.style.display = 'none';
    step4.style.display = 'block';
    showAlert('alert-photo','Foto confirmada e enviada ao robô!');
  } else {
    showAlert('alert-photo','Erro no envio ao robô');
  }
});
