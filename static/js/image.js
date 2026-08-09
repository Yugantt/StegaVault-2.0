/*==========================================
        STEGAVAULT 3.0 IMAGE PAGE
==========================================*/

// ===============================
// IMAGE PREVIEW
// ===============================

function previewImage(inputId, previewId){

    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    if(!input || !preview) return;

    input.addEventListener("change", function(){

        if(this.files && this.files[0]){

            const reader = new FileReader();

            reader.onload = function(e){

                preview.src = e.target.result;
                preview.style.display = "block";

                // Show selected filename
                const span = input.parentElement.querySelector("span");

                if(span){
                    span.innerText = input.files[0].name;
                }

            };

            reader.readAsDataURL(this.files[0]);

        }

    });

}

previewImage("encodeImage","encodePreview");
previewImage("decodeImage","decodePreview");


// ===============================
// CHARACTER COUNTER
// ===============================

const messageBox = document.getElementById("messageBox");
const charCount = document.getElementById("charCount");

if(messageBox && charCount){

    charCount.innerText = messageBox.value.length;

    messageBox.addEventListener("input",function(){

        charCount.innerText = this.value.length;

    });

}


// ===============================
// COPY BUTTON
// ===============================

const copyBtn = document.getElementById("copyBtn");

if(copyBtn){

    copyBtn.addEventListener("click",function(){

        const txt = document.getElementById("decodedMessage");

        if(!txt || txt.value.trim()===""){

            alert("No decoded message available.");
            return;

        }

        navigator.clipboard.writeText(txt.value)

        .then(()=>{

            copyBtn.innerHTML =
            '<i class="fas fa-check"></i> Copied';

            setTimeout(()=>{

                copyBtn.innerHTML =
                '<i class="fas fa-copy"></i> Copy';

            },2000);

        })

        .catch(()=>{

            alert("Copy failed.");

        });

    });

}
// ===============================
// SHOW / HIDE SECRET MESSAGE
// ===============================

const toggleBtn = document.getElementById("toggleBtn");
const decodedMessage = document.getElementById("decodedMessage");

if(toggleBtn && decodedMessage){

    // Hide message initially
    decodedMessage.style.webkitTextSecurity = "disc";

    let hidden = true;

    toggleBtn.innerHTML =
    '<i class="fas fa-eye"></i> Show';

    toggleBtn.addEventListener("click",function(){

        if(decodedMessage.value.trim()===""){
            return;
        }

        if(hidden){

            decodedMessage.style.webkitTextSecurity = "none";

            toggleBtn.innerHTML =
            '<i class="fas fa-eye-slash"></i> Hide';

            hidden = false;

        }else{

            decodedMessage.style.webkitTextSecurity = "disc";

            toggleBtn.innerHTML =
            '<i class="fas fa-eye"></i> Show';

            hidden = true;

        }

    });

}


// ===============================
// DRAG & DROP
// ===============================
document.querySelectorAll(".upload-box").forEach(box=>{

    const input = box.querySelector("input");
    const label = box.querySelector(".upload-label");

    box.addEventListener("dragover",function(e){

        e.preventDefault();

        label.style.borderColor="#38bdf8";
        label.style.background="rgba(56,189,248,.15)";

    });

    box.addEventListener("dragleave",function(){

        label.style.borderColor="";
        label.style.background="";

    });

    box.addEventListener("drop",function(e){

        e.preventDefault();

        input.files=e.dataTransfer.files;

        input.dispatchEvent(new Event("change"));

        label.style.borderColor="";
        label.style.background="";

    });

});

// ===============================
// BUTTON LOADING EFFECT
// ===============================

document.querySelectorAll("form").forEach(form=>{

    form.addEventListener("submit",function(){

        const btn = this.querySelector(".primary-btn");

        if(!btn) return;

        btn.disabled = true;

        btn.dataset.original = btn.innerHTML;

        btn.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Processing...';

        // Restore if request doesn't redirect
        setTimeout(function(){

            btn.disabled = false;

            btn.innerHTML = btn.dataset.original;

        },15000);

    });

});