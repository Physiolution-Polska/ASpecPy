var page = document.getElementById('data-table').getAttribute('data-page')

$('#table-content').load(page, function(){
	var links = document.getElementsByTagName("li")
	var link_name = ''
	for (var i = 0; i < links.length; i++){
		link_name = 'table' + links[i].innerText
		links[i].id = link_name
		$('#'+links[i].id).on('click', function(e) {
			e.preventDefault();
			load_js(e.target.attributes.href.value)
		});
		link_name = ''
	}
});

function load_js(page){
	document.getElementById('data-table').remove()
	var head= document.getElementsByTagName('head')[0];
	var script= document.createElement('script');
	script.src= '../static/js/table.js';
	script.id = 'data-table'
	script.setAttribute('data-page', page)
	head.appendChild(script);
}
