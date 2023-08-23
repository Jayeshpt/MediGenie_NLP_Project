const uploadForm = document.getElementById('uploadForm');
const dropArea = document.querySelector('.drag-area');
const browseButton = document.getElementById('browseButton');
const fileInput = document.getElementById('fileInput');
const submitButton = document.getElementById('submitButton');

browseButton.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        submitButton.removeAttribute('disabled');
        dropArea.classList.add('active');
        showFile(file);
    }
});

dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.classList.add('active');
});

dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('active');
});

dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
        submitButton.removeAttribute('disabled');
        dropArea.classList.add('active');
        showFile(file);
    }
});

function showFile(file) {
    const fileType = file.type;
    const validExtensions = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
    ];
    const maxSize = 200 * 1024 * 1024; // 200MB in bytes

    if (validExtensions.includes(fileType) && file.size <= maxSize) {
        const fileTag = `<div>${file.name}</div>`;
        dropArea.innerHTML = fileTag;
    } else {
        alert('Invalid File! Please upload an xlsx, xls, or csv file up to 200MB in size.');
        dropArea.classList.remove('active');
        fileInput.value = ''; // Reset input value
        submitButton.setAttribute('disabled', true);
    }
}

function name(params) {
    console.log(params);
}

uploadForm.onsubmit = function(event) {
    event.preventDefault();
    const csrfToken = document.getElementsByName('csrfmiddlewaretoken');


    dropArea.innerHTML = 'Uploading . . . ';

    // Get the files from the input
    var files = fileInput.files;

    // Create a FormData object.
    var formData = new FormData();

    //Grab only one file since this script disallows multiple file uploads.
    var file = files[0]; 

    

    if (file.size >= 200000000 ) {
        dropArea.innerHTML = 'You cannot upload this file because its size exceeds the maximum limit of 200 MB.';
        return;
    }

     // Add the file to the AJAX request.
    formData.append('file', file, file.name);
    formData.append('csrfmiddlewaretoken', csrfToken[0].value);

    // Set up the request.
    var xhr = new XMLHttpRequest();

    // Open the connection.
    xhr.open('POST', '/upload/', true);


    // Set up a handler for when the task for the request is complete.
    xhr.onload = function () {
      if (xhr.status === 200) {
        let s = 3
        setInterval(() => {
        dropArea.innerHTML = `<p>Your upload is successful..</p>
            <p>Redireting you in ${s} seconds</p>
        `;
        s--;
        if(s==0){
            window.location.href = '/'
        }
        }, 1000);
      } else {
        dropArea.innerHTML = 'An error occurred during the upload. Try again.';
      }
    };

    // Send the data.
    xhr.send(formData);
}