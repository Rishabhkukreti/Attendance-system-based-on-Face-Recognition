const searchform=document.querySelector('#search-form');
const searchinput=searchform.querySelector('input');


const SpeechRecognition = window.SpeechRecognition || webkitSpeechRecognition;

if(SpeechRecognition){
    console.log("Your Browser supports speech Recognition");
    searchform.insertAdjacentHTML("beforeend",'<button type="button"><i class="fa fa-microphone"></i></button>');
    const mic=searchform.querySelector('button');
    const micicon=mic.querySelector('i');

    const recognition= new SpeechRecognition();
    recognition.continuous=true;

    mic.addEventListener("click",micclick);
    function micclick(){
        if(micicon.classList.contains("fa-microphone")){
            recognition.start();
        }
        else{ 
            recognition.stop();
        }
    }
    recognition.addEventListener("start",startSpeechRecognition);
    recognition.addEventListener("end",endSpeechRecognition);
    recognition.addEventListener("result",speechRecognitionresults);
    function startSpeechRecognition(){
        searchinput.focus();
        micicon.classList.remove("fa-microphone");
        micicon.classList.add("fa-microphone-slash");
    }

    function endSpeechRecognition(){
        micicon.classList.remove("fa-microphone-slash");
        micicon.classList.add("fa-microphone");
        searchinput.focus();
    }
    function speechRecognitionresults(event){
        const currentIndex=event.resultIndex;
        transcript=event.results[currentIndex][0].transcript;
        searchinput.value=transcript;
        searchform.submit();
    }
}
else{
    console.log("Your Browser does not support speech Recognition");
}