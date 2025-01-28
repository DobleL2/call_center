SELECT
    jun.cod_junta,
    jun.id_junta,
    prov.cod_provincia,
    prov.nom_provincia AS provincia,
    isnull(
        circ.cod_circunscripcion,
        '0'
    ) AS cod_circunscripcion,
    isnull(
        circ.nom_circunscripcion,
        '-'
    ) AS circunscripcion,
    cant.cod_canton,
    cant.nom_canton AS canton,
    parr.cod_parroquia,
    parr.nom_parroquia AS parroquia,
    zon.cod_zona,
    zon.nom_zona AS zona,
    rec.cod_recinto,
    rec.nom_recinto AS recinto,
    junta,
    sexo,
    frm.cedula,
    frm.nombres,
    frm.apellidos,
    frm.correo,
    frm.operadora_celular,
    frm.num_celular,
    frm.referido,
    frm.parroquia_direccion
FROM
    provincia prov
    JOIN junta jun
    ON prov.cod_provincia = jun.cod_provincia
    LEFT JOIN circunscripcion circ
    ON jun.cod_provincia = circ.cod_provincia
    AND jun.cod_circunscripcion = circ.cod_circunscripcion
    JOIN canton cant
    ON cant.cod_canton = jun.cod_canton
    JOIN parroquia parr
    ON parr.cod_parroquia = jun.cod_parroquia
    JOIN zona zon
    ON parr.cod_parroquia = zon.cod_parroquia
    AND zon.cod_zona = jun.cod_zona
    JOIN recintos rec
    ON jun.cod_recinto = rec.cod_recinto
    LEFT JOIN formulario_control_electoral frm
	ON frm.cod_junta = jun.cod_junta