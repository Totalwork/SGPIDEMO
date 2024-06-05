use sinin41

select c.id,c.nombre, c.numero, c.descripcion, e.nombre as contratante,
ct.nombre as contratista,et.nombre as estado, mc.nombre as macro_contrato,
t.nombre as tipo, 
(STUFF((select ct.nombre
from proyecto_proyecto_contrato as pc
inner join contrato as c2 on c2.id=pc.contrato_id
inner join empresa_empresa as ct on c2.contratista_id=ct.id
where pc.proyecto_id=(select top 1 pc.proyecto_id from proyecto_proyecto_contrato as pc where pc.contrato_id=c.id) 
and c2.tipo_contrato_id=9
FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 1, '')) as interventor

from contrato as c
inner join empresa_empresa as e on c.contratante_id=e.id
inner join empresa_empresa as ct on c.contratista_id=ct.id
inner join estado_estado as et on c.estado_id=et.id
inner join contrato as mc on c.mcontrato_id=mc.id
inner join tipo_tipo as t on c.tipo_contrato_id=t.id

