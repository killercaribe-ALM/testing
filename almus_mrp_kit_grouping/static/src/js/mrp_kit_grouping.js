/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useState } from "@odoo/owl";

export class AlmusKitTreeRenderer extends ListRenderer {
    setup() {
        super.setup();
        // Estado para controlar qué kits están colapsados
        this.state = useState({
            collapsedKits: new Set(),
        });
        
        // Obtener configuración de colapsar por defecto
        this._loadDefaultCollapseState();
    }
    
    async _loadDefaultCollapseState() {
        try {
            const result = await this.env.services.rpc("/web/dataset/call_kw", {
                model: "ir.config_parameter",
                method: "get_param",
                args: ["almus_mrp_kit_grouping.collapse_by_default"],
                kwargs: {},
            });
            
            if (result === "True") {
                // Colapsar todos los kits por defecto
                const records = this.props.list.records;
                records.forEach(record => {
                    if (!record.data.almus_parent_kit_id) {
                        // Es un kit principal, verificar si tiene hijos
                        const hasChildren = this._hasChildren(record);
                        if (hasChildren) {
                            this.state.collapsedKits.add(record.id);
                        }
                    }
                });
            }
        } catch (error) {
            console.error("Error loading collapse state:", error);
        }
    }
    
    _hasChildren(kitRecord) {
        const records = this.props.list.records;
        return records.some(r => 
            r.data.almus_parent_kit_id && 
            r.data.almus_parent_kit_id[0] === kitRecord.data.product_id[0]
        );
    }
    
    _getVisibleRecords() {
        const records = this.props.list.records;
        const visibleRecords = [];
        const collapsedKitProducts = new Set();
        
        // Identificar qué productos kit están colapsados
        records.forEach(record => {
            if (this.state.collapsedKits.has(record.id) && !record.data.almus_parent_kit_id) {
                collapsedKitProducts.add(record.data.product_id[0]);
            }
        });
        
        // Filtrar registros visibles
        records.forEach(record => {
            const parentKitId = record.data.almus_parent_kit_id;
            
            if (!parentKitId) {
                // Es un registro de nivel superior, siempre visible
                visibleRecords.push(record);
            } else {
                // Verificar si algún kit padre está colapsado
                let isVisible = true;
                
                // Verificar toda la cadena de padres
                if (collapsedKitProducts.has(parentKitId[0])) {
                    isVisible = false;
                } else {
                    // Verificar si hay kits padres en niveles superiores colapsados
                    const parentRecord = records.find(r => 
                        r.data.product_id[0] === parentKitId[0]
                    );
                    
                    if (parentRecord && parentRecord.data.almus_parent_kit_id) {
                        // Recursivamente verificar padres
                        if (collapsedKitProducts.has(parentRecord.data.almus_parent_kit_id[0])) {
                            isVisible = false;
                        }
                    }
                }
                
                if (isVisible) {
                    visibleRecords.push(record);
                }
            }
        });
        
        return visibleRecords;
    }
    
    toggleKit(record) {
        if (this.state.collapsedKits.has(record.id)) {
            this.state.collapsedKits.delete(record.id);
        } else {
            this.state.collapsedKits.add(record.id);
        }
    }
    
    getCellClass(column, record) {
        let classes = super.getCellClass(column, record);
        
        // Agregar clase especial para la primera columna de kits
        if (column === this.state.columns[0] && !record.data.almus_parent_kit_id) {
            const hasChildren = this._hasChildren(record);
            if (hasChildren) {
                classes += " almus-kit-header";
                if (this.state.collapsedKits.has(record.id)) {
                    classes += " collapsed";
                } else {
                    classes += " expanded";
                }
            }
        }
        
        // Agregar indentación para componentes
        if (record.data.almus_bom_level > 0) {
            classes += ` almus-indent-level-${record.data.almus_bom_level}`;
        }
        
        return classes;
    }
    
    onCellClicked(record, column, ev) {
        // Si es la primera columna y es un kit con hijos, toggle
        if (column === this.state.columns[0] && !record.data.almus_parent_kit_id) {
            if (this._hasChildren(record)) {
                ev.stopPropagation();
                ev.preventDefault();
                this.toggleKit(record);
                return;
            }
        }
        
        super.onCellClicked(record, column, ev);
    }
    
    get visibleRecords() {
        return this._getVisibleRecords();
    }
}

// CSS personalizado
const style = document.createElement("style");
style.textContent = `
    .o_list_table .almus-kit-header {
        cursor: pointer;
        font-weight: 600;
        background-color: rgba(0, 123, 255, 0.05);
    }
    
    .o_list_table .almus-kit-header:hover {
        background-color: rgba(0, 123, 255, 0.1);
    }
    
    .o_list_table .almus-kit-header.collapsed::before {
        content: "▶ ";
        padding-right: 5px;
    }
    
    .o_list_table .almus-kit-header.expanded::before {
        content: "▼ ";
        padding-right: 5px;
    }
    
    .o_list_table .almus-indent-level-1 td:first-child {
        padding-left: 30px !important;
    }
    
    .o_list_table .almus-indent-level-2 td:first-child {
        padding-left: 60px !important;
    }
    
    .o_list_table .almus-indent-level-3 td:first-child {
        padding-left: 90px !important;
    }
    
    .o_list_table tr[data-almus-parent-kit] {
        background-color: rgba(0, 0, 0, 0.02);
    }
`;
document.head.appendChild(style);

// Registrar el renderer personalizado
registry.category("views").add("almus_kit_tree", {
    ...registry.category("views").get("list"),
    Renderer: AlmusKitTreeRenderer,
});