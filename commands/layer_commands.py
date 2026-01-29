"""
Layer management commands for QGIS AI Bridge

Handles layer operations: list, add, remove, set_active, set_visible, reorder, get_info
"""

from qgis.core import QgsProject, QgsMapLayer


def layer_list(params):
    """
    List all layers in the current QGIS project

    Args:
        params (dict): Command parameters
            - include_metadata (bool, optional): Include detailed metadata (default: True)

    Returns:
        dict: {
            "success": bool,
            "layers": list of layer info dicts,
            "count": int
        }
    """
    try:
        from PyQt5.QtWidgets import QApplication

        include_metadata = params.get('include_metadata', True)
        project = QgsProject.instance()
        layers = []

        # Get all layers from project
        for layer_id, layer in project.mapLayers().items():
            layer_info = {
                "id": layer.id(),
                "name": layer.name(),
                "type": layer.type().name if hasattr(layer.type(), 'name') else str(layer.type()),
                "is_valid": layer.isValid()
            }

            # Get visibility from layer tree
            layer_tree_layer = project.layerTreeRoot().findLayer(layer.id())
            if layer_tree_layer:
                layer_info["is_visible"] = layer_tree_layer.isVisible()
            else:
                layer_info["is_visible"] = None

            # Add detailed metadata if requested
            if include_metadata:
                # CRS
                if layer.crs().isValid():
                    layer_info["crs"] = layer.crs().authid()
                    layer_info["crs_description"] = layer.crs().description()
                else:
                    layer_info["crs"] = "N/A"
                    layer_info["crs_description"] = "No CRS"

                # Extent
                if layer.extent():
                    extent = layer.extent()
                    layer_info["extent"] = {
                        "xmin": extent.xMinimum(),
                        "ymin": extent.yMinimum(),
                        "xmax": extent.xMaximum(),
                        "ymax": extent.yMaximum()
                    }
                else:
                    layer_info["extent"] = None

                # Feature count (for vector layers)
                if hasattr(layer, 'featureCount'):
                    layer_info["feature_count"] = layer.featureCount()
                else:
                    layer_info["feature_count"] = None

                # Source
                layer_info["source"] = layer.source()

                # Provider type
                if hasattr(layer, 'providerType'):
                    layer_info["provider"] = layer.providerType()
                else:
                    layer_info["provider"] = None

            layers.append(layer_info)

        QApplication.processEvents()

        return {
            "success": True,
            "layers": layers,
            "count": len(layers)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
