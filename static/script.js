const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const submitBtn = document.getElementById('submitBtn');
const imageData = document.getElementById('imageData');

navigator.mediaDevices.getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;
  });

captureBtn.addEventListener('click', () => {
  const context = canvas.getContext('2d');
  canvas.style.display = 'block';
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const dataURL = canvas.toDataURL('image/png');
  imageData.value = dataURL;

  submitBtn.style.display = 'inline-block';
});
