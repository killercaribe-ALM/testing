# Almus Tipos de Documento Venezuela

## Descripción

Módulo de localización venezolana para Odoo 18 que agrega la funcionalidad de tipos de documento fiscal según las normativas del SENIAT. Este módulo forma parte del ecosistema Almus y permite especificar el tipo de documento (V, E, J, G, P, C) en los contactos, complementando el campo estándar de identificación fiscal de Odoo.

## Características

- ✅ **Campo de selección con tipos oficiales del SENIAT**: Agrega un campo de selección antes del número de identificación fiscal
- ✅ **Integración nativa**: Se integra perfectamente con el formulario estándar de contactos de Odoo
- ✅ **Validación configurable**: Opción para validar el formato del RIF venezolano (7-9 dígitos)
- ✅ **Configuración centralizada**: Todas las opciones disponibles desde el panel Almus en Configuración
- ✅ **Filtros de búsqueda**: Permite filtrar contactos por tipo de documento
- ✅ **Logging integrado**: Registra cambios para auditoría

## Requisitos

- Odoo 18.0 o superior
- Módulo `almus_base` instalado
- Módulos base: `base`, `contacts`

## Instalación

1. Clonar o descargar este módulo en tu directorio de addons de Odoo
2. Actualizar la lista de aplicaciones en Odoo
3. Buscar "Almus Tipos de Documento Venezuela" en Apps
4. Instalar el módulo

## Configuración

### Acceder a la configuración

1. Ir a **Configuración → Ajustes**
2. Buscar la sección **Almus Dev**
3. Encontrar **Tipos de Documento Venezuela**

### Opciones disponibles

- **Validar formato de documento venezolano**: Activa la validación automática del formato (7-9 dígitos numéricos)
- **Tipo de documento obligatorio**: Hace obligatorio seleccionar el tipo cuando se ingresa un número fiscal

## Tipos de Documento Disponibles

| Código | Descripción | Uso |
|--------|-------------|-----|
| **V** | Venezolano | Personas naturales venezolanas |
| **E** | Extranjero | Personas naturales extranjeras |
| **J** | Jurídico | Empresas y personas jurídicas |
| **G** | Gobierno | Entidades gubernamentales |
| **P** | Pasaporte | Identificación por pasaporte |
| **C** | Comuna/Consejo Comunal | Organizaciones comunitarias |

## Uso

### En el formulario de contactos

1. Al crear o editar un contacto, encontrarás el campo **Tipo de Documento** antes del campo **NIF**
2. Selecciona el tipo apropiado según el contacto
3. Ingresa el número de documento en el campo NIF (solo números)

### Búsqueda y filtros

El módulo agrega los siguientes filtros en la vista de búsqueda de contactos:

- **Documentos Venezolanos**: Muestra todos los contactos con tipo de documento venezolano
- **Personas Naturales (V/E)**: Filtra solo personas naturales
- **Personas Jurídicas (J/G/C)**: Filtra entidades jurídicas
- **Agrupar por Tipo de Documento**: Agrupa los resultados por tipo

## Validaciones

Cuando la validación está activada:

- Solo se permiten números en el campo de identificación fiscal
- La longitud debe estar entre 7 y 9 dígitos
- Se muestra un mensaje de error claro si el formato es incorrecto

## Estructura Técnica

```
l10n_ve_almus_document_type/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_partner.py              # Extiende el modelo de contactos
│   └── res_config_settings.py      # Configuración del módulo
├── views/
│   ├── res_partner_views.xml       # Vistas de contactos
│   └── res_config_settings_views.xml # Vista de configuración
├── security/
│   └── ir.model.access.csv         # Permisos de acceso
└── static/
    └── description/
        └── icon.png                # Icono del módulo

```

## Desarrollo y Contribuciones

Este módulo sigue las convenciones de desarrollo del ecosistema Almus:

- Nomenclatura con prefijo `l10n_ve_almus_`
- Dependencia obligatoria de `almus_base`
- Integración con el panel de configuración Almus
- Código simple y mantenible

## Soporte

Para soporte y consultas:
- Web: [www.almus.dev](https://www.almus.dev)
- Desarrollado por: Almus Dev (JDV-ALM)

## Licencia

LGPL-3

---

*Módulo parte del ecosistema Almus para Odoo 18*