# Estructura del proyecto :classical_building:

Orden de carpetas y sus funciones

## Carpetas :card_file_box:
```text
├── apps                        # Todas las aplicaciones del proyecto
│ ├── emails                    # Configurar el servicio para enviar correos
│ │ └── services
│ ├── graphql                   # Consultas graphql, para querys necesarias
│ │ ├── management
│ │ ├── management_user
│ │ └── school
│ ├── management                # Lógica de administración de los datos de una escuela
│ │ ├── admin.py
│ │ ├── apiv1
│ │ │ ├── school                # Información relacionada con la escuela
│ │ │ └── user                  # Información relacionada con usuarios y sus permisos
│ │ └── services
│ ├── school                    # Modela toda la información de una escuela
│ │ ├── admin.py
│ │ ├── apiv1
│ │ └── services
│ ├── user                     # Creación/actualización/eliminación de un usuario
│ │ ├── apiv1
│ │ └── services
│ └── utils
├── docs                       # Documentación del proyecto
├── manage.py
├── README.md
├── requirements.txt          # Requerimientos del proyecto
├── school                    # Configuraciones relacionadas con el proyecto
└── tests                     # Tests de las aplicaciones/funciones del proyecto
    ├── emails
    ├── graphql
    │ ├── management
    │ ├── management_user
    │ └── school
    ├── management
    ├── school
    ├── user
    └── utils
```

-----

### Aplicaciones :jigsaw:

**emails**: El propósito de esta aplicación es configurar el servicio de correos que se usará en el proyecto:
- Formato del mensaje
- Contenido del mensaje
- Remitente
- Envío del correo


**graphql**: Todas las querys de graphql se encuentran de esta app.\
Organizadas por características  y está, a su vez, por el tipo de consulta:  
- management
- management_user
- school

Entre las diferentes consultas que se pueden presentar se tienen:\
- *querys*: Para obtener información. Una o de múltiples fuentes.
- *mutations*: Para <ins>crear/modificar</ins> información. Por los momentos, solo se usan para crear información.


**management**: Aquí está toda la lógica de administración de información de una escuela.\
Pasando por:
- *Crear/Actualizar/Eliminar* datos relacionados con la escuela.  
- *Agregar/Eliminar* permisos de usuarios.  


También, permite definir límites de acceso a la información de una escuela, ya que un usuario, aunque tenga permisos para eliminar datos, no podrá hacerlo si esa información forma parte de la administración a la que no pertence, en otras palabras, información que pertenece a otro colegio.  

**school**: Aquí se moldea toda la información que tendrá una escuela.
Tablas, tipos de columnas, validaciones de datos para las columnas, relación entre tablas.  

De esta aplicación nos aprovechamos para tener un panel de administración que nos permita ver qué escuela (y sus datos relacionados) forman parte de nuestro servicio.\
Esto es solo exclusivo para nosotros, y nos otorga obviamente una mayor cantidad de privilegios o permisos.  

**user**: Se moldea los datos que posee un usuario (su tabla en la base de datos).
- Actualizar/Eliminar datos de un usuario.  

El sistema de login, está relacionado con esta aplicación.  
Consiste en un sistema de validación basado en **JWTokens**, por lo tanto, aquí también se otorgan o validan tokens de acceso.  


Este documento presenta un modelo básico de la documentación del proyecto, **probablemente no forme parte de la documentación final**, ya que el proyecto se encuentra en desarrollo.