bl_info = {
    "name": "Blender to Clip Studio Link",
    "author": "X(twitter)@cblpan",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "Image Editor > Sidebar > CSP Tab",
    "description": "Send Texture and UV layout to Clip Studio Paint directly with auto-sized UV.",
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
        # 애드온 이름 찾기
        addon_name = __package__ if __package__ else __name__.partition('.')[0]
        
        try:
            preferences = context.preferences.addons[addon_name].preferences
        except KeyError:
            self.report({'ERROR'}, "Add-on not found. Please Install the file properly.")
            return {'CANCELLED'}

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

        # [수정됨] 이미지의 현재 해상도 가져오기 (가로, 세로)
        img_width, img_height = img.size

        # UV 맵 내보내기 로직
        obj = context.active_object
        uv_path = ""
        
        if obj and obj.type == 'MESH':
            base_dir = os.path.dirname(filepath)
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            uv_filename = f"{file_name}_UV.png"
            uv_path = os.path.join(base_dir, uv_filename)
            
            prev_mode = obj.mode
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            
            try:
                # [수정됨] 고정 사이즈(2048) 대신 이미지의 실제 사이즈(img_width, img_height) 적용
                bpy.ops.uv.export_layout(filepath=uv_path, size=(img_width, img_height), opacity=0.25)
            except Exception as e:
                self.report({'WARNING'}, f"UV Export Failed: {e}")
                uv_path = ""
            
            bpy.ops.object.mode_set(mode=prev_mode)

        # 실행 (Clip Studio Paint 열기)
        try:
            file_list = [csp_exec_path, filepath]
            if uv_path and os.path.exists(uv_path):
                file_list.append(uv_path)
                
            subprocess.Popen(file_list)
            self.report({'INFO'}, f"Sent to Clip Studio! (Size: {img_width}x{img_height})")
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
        # UI 버튼 이름과 실제 기능 연결
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
