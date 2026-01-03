bl_info = {
    "name": "Blender to Clip Studio Link",
    "author": "X(twitter)@cblpan",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "Image Editor > Sidebar > CSP Tab",
    "description": "Send Texture and UV layout to Clip Studio Paint directly.",
    "warning": "",
    "wiki_url": "",
    "category": "Image",
}

import bpy
import os
import subprocess

# --- 1. 사용자 환경 설정 (Preferences) 클래스 ---
class CSPLinkPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # 사용자가 경로를 직접 선택할 수 있는 파일 탐색기 속성
    csp_path: bpy.props.StringProperty(
        name="Clip Studio Path",
        subtype='FILE_PATH',
        default=r"C:\Program Files\CELSYS\CLIP STUDIO 1.5\CLIP STUDIO PAINT\ClipStudioPaint.exe",
        description="Path to ClipStudioPaint.exe"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Select your Clip Studio Paint Executable (.exe):")
        layout.prop(self, "csp_path")

# --- 2. 기능 구현 (Operator) ---
class IMAGE_OT_OpenInCSP(bpy.types.Operator):
    """Open Texture and UV in Clip Studio Paint"""
    bl_idname = "image.open_in_csp"
    bl_label = "Open Texture & UV"
    
    def execute(self, context):
        # 환경 설정에서 사용자가 지정한 경로 가져오기
        preferences = context.preferences.addons[__package__].preferences
        csp_exec_path = preferences.csp_path

        # 경로 유효성 검사
        if not os.path.exists(csp_exec_path):
            self.report({'ERROR'}, "Clip Studio path is incorrect. Check Add-on Preferences.")
            return {'CANCELLED'}

        # 이미지 확인
        img = context.edit_image
        if not img:
            self.report({'ERROR'}, "No image selected.")
            return {'CANCELLED'}
            
        filepath = bpy.path.abspath(img.filepath)
        if not os.path.exists(filepath):
            self.report({'ERROR'}, "Save the image file first.")
            return {'CANCELLED'}

        # UV 맵 내보내기 로직
        obj = context.active_object
        uv_path = ""
        
        if obj and obj.type == 'MESH':
            base_dir = os.path.dirname(filepath)
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            uv_filename = f"{file_name}_UV.png"
            uv_path = os.path.join(base_dir, uv_filename)
            
            # 현재 모드 저장 및 에딧 모드 전환
            prev_mode = obj.mode
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            
            try:
                # UV 내보내기 (2048px, 투명도 0.25)
                bpy.ops.uv.export_layout(filepath=uv_path, size=(2048, 2048), opacity=0.25)
            except Exception as e:
                self.report({'WARNING'}, f"UV Export Failed: {e}")
                uv_path = ""
            
            # 원래 모드로 복귀
            bpy.ops.object.mode_set(mode=prev_mode)

        # 실행 (경로 + 이미지 + UV)
        try:
            file_list = [csp_exec_path, filepath]
            if uv_path and os.path.exists(uv_path):
                file_list.append(uv_path)
                
            subprocess.Popen(file_list)
            self.report({'INFO'}, f"Sent to Clip Studio!")
        except Exception as e:
            self.report({'ERROR'}, f"Execution Failed: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

# --- 3. UI 패널 ---
class IMAGE_PT_CSPPanel(bpy.types.Panel):
    bl_label = "CSP Link"
    bl_idname = "IMAGE_PT_csp_panel"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'CSP' 

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("image.open_in_csp", icon='BRUSH_DATA', text="Open in CSP")
        col.operator("image.reload", icon='FILE_REFRESH', text="Reload Image")

# --- 등록부 ---
classes = (
    CSPLinkPreferences,
    IMAGE_OT_OpenInCSP,
    IMAGE_PT_CSPPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

# This script was generated with the assistance of Google Gemini.
# AI의 도움으로 작성된 스크립트입니다.