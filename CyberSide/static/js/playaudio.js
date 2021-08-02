var audio = document.getElementById("cyberside_ambience");
var not_played = true;
audio.volume = 0.1;

(function init_sound(){
	if(not_played){
		audio.play();
	}
}());

document.addEventListener("click", function(event) {
	if(not_played){
		not_played = false;
		audio.play();
	}

});