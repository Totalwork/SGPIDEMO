//Buscar fecha Inicio del contrato
function fechasInicio(vigencias){
	var fecha = null;
	ko.utils.arrayForEach(vigencias,function(p){
		if (p.tipo.id == contratoVigencia.tipoV.contrato()) {
			fecha = p.fecha_inicio;
		}
		//console.log("sdsd:"+contratoVigencia.tipoV.contrato());
	});
	ko.utils.arrayForEach(vigencias,function(p){
		if ((p.tipo.id == contratoVigencia.tipoV.replanteo() && (p.fecha_inicio))){
			fecha = p.fecha_inicio;
		}
	});
	return fecha;
}

//Buscar fecha Fin del contrato
function fechasFin(vigencias){
	var fecha = null;
	var a_inicio = '';
	var a_reinicio = '';

	ko.utils.arrayForEach(vigencias,function(p){
		if (p.tipo.id == contratoVigencia.tipoV.contrato()) {
			fecha = p.fecha_fin;

			//console.log(p.)
		}
	});
	ko.utils.arrayForEach(vigencias,function(p){
		if ((p.tipo.id == contratoVigencia.tipoV.replanteo() && (p.fecha_inicio))){
			fecha = p.fecha_fin;
		}
	});
	ko.utils.arrayForEach(vigencias,function(p){
		if (p.tipo.id == contratoVigencia.tipoV.otrosi()){
			if (p.fecha_fin) {
				
				if(fecha < p.fecha_fin){
					fecha = p.fecha_fin;
				}
			}
		}
	});

	ko.utils.arrayForEach(vigencias,function(p){
		if (p.tipo.id == contratoVigencia.tipoV.actaSuspension()){
			a_inicio = p.fecha_inicio;
		}
		if (p.tipo.id == contratoVigencia.tipoV.actaReinicio()){
			a_reinicio = p.fecha_inicio;
		}

		// Sacar los dias que duro suspendidos
		if((a_inicio != '') && (a_reinicio != '')){

			var inicio = new Date(a_inicio+" 00:00:00");
			var fin = new Date(a_reinicio+" 00:00:00");
			var f_fin = new Date(fecha+" 00:00:00");

			var fechaResta = fin - inicio;
			var fechaResta = (((fechaResta / 1000) / 60) / 60) / 24;
			//console.log("fechaResta: "+fechaResta);

			f_fin.setDate (f_fin.getDate() + fechaResta);
			fecha = f_fin.getFullYear()+'-'+(f_fin.getMonth()+1)+'-'+f_fin.getDate();
			a_inicio = '';
			a_reinicio = '';
		}
	});
	return fecha;
}
