const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const confirmarBtn = document.getElementById('confirmarBtn');
const fotoBtn = document.getElementById('fotoBtn');

let alturaConfirmada = false;

// Acessar webcam
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => {
    alert("Erro ao acessar a câmera: " + err);
  });

// Alerta verde de sucesso
function mostrarSucesso(msg) {
  const alerta = document.getElementById('alerta-sucesso');
  alerta.textContent = "✔️ " + msg;
  alerta.classList.remove('oculto');
  setTimeout(() => {
    alerta.classList.add('oculto');
  }, 3000);
}

// Alerta vermelho de erro
function mostrarErro(msg) {
  const alerta = document.getElementById('alerta-erro');
  alerta.textContent = "❌ " + msg;
  alerta.classList.remove('oculto');
  setTimeout(() => {
    alerta.classList.add('oculto');
  }, 3000);
}

// Aplica chroma key branco
function aplicarFundoBranco() {
  const ctx = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const frame = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = frame.data;

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];

    if (r > 180 && g > 180 && b > 180) {
      data[i] = 255;
      data[i + 1] = 255;
      data[i + 2] = 255;
    }
  }

  ctx.putImageData(frame, 0, 0);

  const link = document.createElement('a');
  link.download = 'img/fotopessoa.png';  // Simula pasta
  link.href = canvas.toDataURL('image/png');
  link.click();
}

// Confirmar altura
confirmarBtn.addEventListener('click', () => {
  const altura = document.getElementById('altura').value;
  if (!altura || altura <= 0) {
    mostrarErro("Por favor, insira uma altura válida.");
    return;
  }

  mostrarSucesso(`Altura confirmada: ${altura} cm.`);
  alturaConfirmada = true;
  fotoBtn.disabled = false;
});

// Tirar foto
fotoBtn.addEventListener('click', () => {
  if (!alturaConfirmada) {
    mostrarErro("Confirme a altura antes de tirar a foto.");
    return;
  }

  const canvas = document.getElementById('canvas');
  const blob = dataURItoBlob(canvas.toDataURL('image/png'));
  const formData = new FormData();
  formData.append('image', blob, 'fotopessoa.png');

  fetch('http://localhost:5000/upload', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(msg => {
    console.log(msg);
    mostrarSucesso("Imagem processada e enviada ao robô!");
  })
  .catch(err => {
    console.error(err);
    mostrarErro("Erro ao enviar imagem.");
  });
});

// Função auxiliar para converter base64 → blob
function dataURItoBlob(dataURI) {
  const byteString = atob(dataURI.split(',')[1]);
  const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  return new Blob([ab], { type: mimeString });
}

