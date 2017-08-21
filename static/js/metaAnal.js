function clickedShowSigCheckbox(){
	if($('#showSigCheckbox').is(':checked')){
		showSigs();
	}
	else{
		hideSigs();
	}
}

function hideSigs(){
	$('.changeableCell').each(function(){
		currentVal = $(this).html();
		if (currentVal.length>1 && currentVal.slice(-2,-1)=="*"){
			newVal = currentVal.slice(0,-3)+")";
			$(this).html(newVal);
		}
	});
}

function showSigs(){
	$('.changeableCell').each(function(){
		$(this).html($(this).data("initial"));
	});
}