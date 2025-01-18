var startDate=document.getElementById("start");
var endDate=document.getElementById("end");
var numberOfGraphic=0;
startDate.max = endDate.max = new Date().toISOString().split("T")[0];
startDate.value = endDate.value = new Date().toISOString().split("T")[0];
setStartDate(1);
switchAnaliticButton("graphic-first");
var isStopped=false
showShpon("el-1")

window.onanimationiteration = console.log;

function setStartDate(days){
  var start_val=new Date();
  start_val.setDate(start_val.getDate()-days);
  startDate.value = start_val.toISOString().split("T")[0];
  console.log(startDate.value);
}

function showShpon(id){
  var viewer = document.getElementById("viewer");
  var viewerText = document.getElementById("shpon-text");
  var element = document.getElementById(id);
  viewer.style.backgroundImage=element.style.backgroundImage;
  viewer.setAttribute("value", element.getAttribute("value"));
  var isDefect = element.getAttribute("value2")
  console.log(isDefect=="b'False'")
  if (isDefect=="b'False'"){
    viewerText.innerHTML = "Нет дефекта";
  }
  else{
    viewerText.innerHTML = "Есть дефект";
  }
}

function dropPanel() {
  document.getElementById("myDropdown").classList.toggle("show");
  console.log('drop')
}
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var openDropdown = dropdowns[0];
    if (openDropdown.classList.contains('show')) {
      openDropdown.classList.remove('show');
    }
  }
}

function switchAnaliticButton(id){
  var buttons = document.getElementsByClassName("analitic");
  var i;
  for (i = 0; i < buttons.length; i++) {
    buttons[i].style.backgroundColor="#F5F5F5";
  }
  document.getElementById(id).style.backgroundColor="rgb(187, 187, 187)";
  if(id=="graphic-first") numberOfGraphic=1;
  if(id=="graphic-second") numberOfGraphic=2;
  if(id=="graphic-third") numberOfGraphic=3;
  console.log(id);
}

function stop(){
  if (isStopped){
    isStopped=false;
    document.getElementById("stop").style.backgroundColor="#97D700CC"; 
    setIndexPost(0, -1, -1);
  }
  else{
    isStopped=true;
    document.getElementById("stop").style.backgroundColor="#88b32a"; 
    setIndexPost( 1, -1, -1);
  }
}
function sendDefect(defect_id){
  var dropdowns = document.getElementsByClassName("dropdown-content");//close drop panel
  var openDropdown = dropdowns[0];
  if (openDropdown.classList.contains('show')) {
    openDropdown.classList.remove('show');
  }
  var defect = defect_id[defect_id.length - 1];
  console.log(defect);
  let ischange = confirm("Изменить характеристику шпона?");
  if (ischange) setIndexPost(2, defect, document.getElementById("viewer").getAttribute("value"));
}
function switchAnaliticTime(id){
  if(id=="graphic-day"){
    setStartDate(1);
  }
  if(id=="graphic-month"){
    setStartDate(30);
  }
  if(id=="graphic-year"){
    setStartDate(365);
  }
}

function setIndexPost(command, defect, id){//0-stop, 1-run, 2-defect
  const xhr = new XMLHttpRequest();
  xhr.open("POST",  '/index', true);
  xhr.setRequestHeader("Content-type", "application/json");
  const body = JSON.stringify(
  {
    'command': command, 
    'shpon_character': defect, 
    'shpon_id': defect, 
  });
  console.log(body);
  xhr.send(body);
}

function sentDate(){
  const xhr = new XMLHttpRequest();
  xhr.open("POST",  '/analitics', true);
  xhr.setRequestHeader("Content-type", "application/json");
  const body = JSON.stringify(
  {
    'start': startDate.value, 
    'end': endDate.value, 
    'num': numberOfGraphic, 
  });
  console.log(body);
  xhr.send(body);

  xhr.onload = function() {
    let path = xhr.response;
    var graphViewer = document.getElementById("analitics-graphic");
    graphViewer.style.backgroundImage="URL({content})".replace("{content}", path)
    console.log(path)
  };
}

document.addEventListener('DOMContentLoaded', function () {
  var socket = io.connect('http://' + document.domain + ':' + location.port);
  console.log('http://' + document.domain + ':' + location.port);
  socket.on('connect', function () {
      console.log('WebSocket connected!');
      socket.emit('my event', {data: 'I\'m connected!'});
  });

  socket.on('message', function (msg) {
      console.log('Message received: ' + msg.data);
  });
});

io.on('connection', (socket) => {
  console.log('//');
  socket.on('hello', (value, callback) => {
    // once the event is successfully handled
    callback();
  });
})