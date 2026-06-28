import requests
import os
import json

# --- CẤU HÌNH ---
GITLAB_URL = "https://gitlab.com"
PARENT_GROUP_PATH = "Group" 
PRIVATE_TOKEN = "glpat-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OUTPUT_DIR = "./gitlab_dump_all"

headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

def save_vars(api_url, folder_name):
    """Tải và lưu Variables"""
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        variables = response.json()
        if not variables: return

        folder_path = os.path.join(OUTPUT_DIR, folder_name.replace('/', '_'))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        for var in variables:
            if var.get('variable_type') == "file":
                file_path = os.path.join(folder_path, f"FILE_{var['key']}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(var['value'])
            
        with open(os.path.join(folder_path, "all_vars.json"), "w", encoding="utf-8") as f:
            json.dump(variables, f, indent=4)
        print(f"    [OK] Đã lưu {len(variables)} biến.")

def get_everything():
    # 1. Lấy thông tin chính xác của Group cha để lấy ID
    encoded_path = PARENT_GROUP_PATH.replace('/', '%2F')
    group_url = f"{GITLAB_URL}/api/v4/groups/{encoded_path}"
    
    res = requests.get(group_url, headers=headers)
    if res.status_code != 200:
        print(f"Lỗi truy cập Group cha: {res.status_code} - {res.text}")
        return

    parent_group = res.json()
    parent_id = parent_group['id']
    
    # 2. Lấy TẤT CẢ Subgroups của Group cha này (Sử dụng tham số để lấy đệ quy)
    # Tham số 'include_subgroups=True' qua API /groups/:id/projects hoặc 
    # lấy danh sách từ /groups/:id/subgroups
    print(f"--- Bắt đầu quét từ Group: {PARENT_GROUP_PATH} (ID: {parent_id}) ---")
    
    # Lưu biến cho Group cha
    save_vars(f"{GITLAB_URL}/api/v4/groups/{parent_id}/variables", f"GROUP_{PARENT_GROUP_PATH}")

    # Lấy danh sách Subgroups
    subgroups_url = f"{GITLAB_URL}/api/v4/groups/{parent_id}/subgroups"
    subgroups = requests.get(subgroups_url, headers=headers, params={"per_page": 100, "all_available": True}).json()

    # Thêm chính group cha vào danh sách xử lý projects
    target_groups = [{"id": parent_id, "full_path": PARENT_GROUP_PATH}] 
    if isinstance(subgroups, list):
        target_groups.extend(subgroups)

    for g in target_groups:
        g_id = g['id']
        g_path = g['full_path']
        
        if g_id != parent_id: # Tránh quét lại group cha
            print(f"\n[*] Xử lý Subgroup: {g_path}")
            save_vars(f"{GITLAB_URL}/api/v4/groups/{g_id}/variables", f"GROUP_{g_path}")

        # 3. Lấy Projects thuộc từng Group/Subgroup
        projects_url = f"{GITLAB_URL}/api/v4/groups/{g_id}/projects"
        projects = requests.get(projects_url, headers=headers, params={"per_page": 100}).json()
        
        if isinstance(projects, list):
            for p in projects:
                print(f"  > Project: {p['path_with_namespace']}")
                save_vars(f"{GITLAB_URL}/api/v4/projects/{p['id']}/variables", f"PROJECT_{p['path_with_namespace']}")

if __name__ == "__main__":
    get_everything()