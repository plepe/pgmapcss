Config options can be set by using {{{@config config_option config_value;}}} in the MapCSS file or as parameters to pgmapcss, by using {{{-c}}} or {{{--config}}}, e.g. {{{pgmapcss --config option1=value1 option2=value2}}}.

The following config options are supported:

|= Config option |= Description |= Possible values
| josm_classes | when 'true', a {{{set foo;}}} statement will also set the class foo (synonymous to {{{set .foo;}}}) | 'true' or 'false' (default)
| angular_system | choose which angular system will be used for trigonometric functions | 'degrees' (default), 'radians'
| db.srs | Spatial Reference System used in the database. Autodetected. | Usual values: 4326 (WGS-84), 900913 resp. 3857 (Spherical Mercator for Web Maps)
| unit.srs | Spatial Reference System to use for distances. If other values than 900913 are used, unexpected behaviour might happen. | 900913
| srs | Default Spatial Reference System to use on the frontend side | 900913 when using with renderer (mode 'database-function'), 4326 otherwise
| offline | When compiling standalone mode, do not make any requests to the database. | true/**false**
| debug.profiler | during execution, show some statistics about query/processing time and count of objects. | true/**false**
| debug.context | show bounding box and scale denominator of requests. | true/**false**
| debug.rusage | show resource usage at end of processing. | true/**false**
| debug.explain_queries | Print queries, their plans and count of executions to stderr (standalone mode only). | true/**false**
