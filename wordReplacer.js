function wordReplace() {
	console.log('Replacing swear words');
	document.body.innerHTML = document.body.innerHTML.replace(/ass/g, “a**”);
}
window.onload = wordReplace;