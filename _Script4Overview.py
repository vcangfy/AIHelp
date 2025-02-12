import os
import shutil
import platform

# 常量定义：目标文件夹
DESTINATION_FOLDER = '_overview4AI'  # 目标文件夹
DESCRIPTION_FILE = '_DetailsForAI.txt'
PROJECT_DESCRIPTION_FILE = '.ProjectDescription.properties'

def is_interesting_file(filename, interesting_extensions):
    """判断是否是需要处理的文件"""

    return any(filename.endswith(ext) for ext in interesting_extensions)


def read_project_description(file_path):
    """读取ProjectDescription.properties文件，返回工程名、项目目的和给AI的提示词"""
    project_name, project_purpose, project_prompt, project_target = "未知工程", "未知目的", "", []

    with open(file_path, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
    
    properties = {}
    for line in lines:
        # 去除行首行尾的空白字符，并跳过空行或注释
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 分割键值对
        key, value = line.split('=', 1)
        properties[key.strip()] = value.strip()

    project_name = properties.get('project.name', "未知工程")
    project_purpose = properties.get('project.purpose', "未知目的")
    project_prompt = properties.get('project.prompt', "")
    project_target = properties.get('project.target', "").split(',')

    return project_name, project_purpose, project_prompt, project_target

def copy_files(src_folders, dest_folder):
    """从多个源文件夹复制特定类型的文件到目标文件夹，并在文件名后附加.txt"""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    for src_folder in src_folders:
        for root, _, files in os.walk(src_folder):
            for file in files:
                if is_interesting_file(file):
                    source_file = os.path.join(root, file)
                    # 在文件名后附加 .txt 后缀，但保留原始文件名
                    target_file = os.path.join(dest_folder, f"{file}.txt")
                    
                    shutil.copy2(source_file, target_file)  # 使用copy2保留文件元数据

def generate_project_tree(project_name, src_folders, dest_folder):
    """生成项目树状结构并保存到_DetailsForAI.txt文件中"""
    description_path = os.path.join(dest_folder, DESCRIPTION_FILE)
    path_sep = '/' if platform.system() == 'Linux' else '\\'
    
    def write_folder_contents(folder_path, indent, file_handle):
        """递归写入文件夹内容"""
        try:
            entries = sorted(os.listdir(folder_path), 
                           key=lambda x: (not os.path.isdir(os.path.join(folder_path, x)), x))
        except PermissionError:
            return

        for entry in entries:
            entry_path = os.path.join(folder_path, entry)
            if os.path.isdir(entry_path):
                write_folder_contents(entry_path, indent + 4, file_handle)
            else:
                if is_interesting_file(entry):
                    file_handle.write(f"{' ' * indent}{entry}\n")

    with open(description_path, 'w', encoding='utf-8') as f:
        f.write(f"# {project_name} - 项目结构\n\n")
        f.write("## ProjectStructure\n\n")
        f.write(f"{project_name}{path_sep}\n")
        f.write("    _Script2Project.py\n")

        for src_folder in src_folders:
            if not os.path.exists(src_folder):
                continue
            folder_name = os.path.basename(os.path.normpath(src_folder))
            f.write(f"    {folder_name}{path_sep}\n")
            write_folder_contents(src_folder, 8, f)  # 初始缩进为8空格

        f.write("\n---\n\n")

def extract_existing_sections(description_path):
    """提取现有的ProjectDescription和PromptToAI部分"""
    existing_sections = {
        "ProjectDescription": "",
        "PromptToAI": ""
    }
    
    with open(description_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "## ProjectDescription" in content:
        pd_start = content.find("## ProjectDescription")
        pd_end = content.find("---", pd_start)
        existing_sections["ProjectDescription"] = content[pd_start:pd_end]
    
    if "## PromptToAI" in content:
        pt_start = content.find("## PromptToAI")
        existing_sections["PromptToAI"] = content[pt_start:]
    
    return existing_sections

def generate_project_description(project_purpose, project_prompt, dest_folder, existing_sections):
    """生成项目描述文件并保存到_DetailsForAI.txt文件中"""
    description_path = os.path.join(dest_folder, DESCRIPTION_FILE)
    
    system_env = platform.system()

    with open(description_path, 'a', encoding='utf-8') as f:
        if "ProjectDescription" in existing_sections and existing_sections["ProjectDescription"]:
            f.write(existing_sections["ProjectDescription"])
        else:
            f.write("## ProjectDescription\n\n")
            f.write(f"Environment: {system_env}\n\n")  # 添加系统环境信息
            f.write(f"Information: \n\n")
            f.write(f"Purpose: {project_purpose}\n\n")
            f.write(f"NextNeeds: \n\n")

        f.write("---\n\n")
        
        if "PromptToAI" in existing_sections and existing_sections["PromptToAI"]:
            f.write(existing_sections["PromptToAI"])
        else:
            f.write("## PromptToAI\n\n")
            f.write(f"{project_prompt}\n\n")

def clean_and_copy_files(dest_folder, src_folders, destination_folder):
    """清理目标文件夹中的非_DetailsForAI.txt文件，并重新生成新的文件副本"""
    for root, dirs, files in os.walk(dest_folder):
        for file in files:
            if file != DESCRIPTION_FILE:
                os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))
    
    copy_files(src_folders, destination_folder)

if __name__ == "__main__":

    # 获取当前脚本的绝对路径和所在目录
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    # 读取ProjectDescription.properties文件
    project_description_path = os.path.join(script_dir, PROJECT_DESCRIPTION_FILE)
    project_name, project_purpose, project_prompt, project_target = read_project_description(project_description_path)
    
    SOURCE_FOLDERS = [folder.strip() for folder in project_target]  # 更新源文件夹列表
    project_sourceFolder_path = []
    for folder in SOURCE_FOLDERS:
    # 使用 os.path.join 将 script_dir 和 folder 名称拼接成完整路径
        full_path = os.path.join(script_dir, folder)
        project_sourceFolder_path.append(full_path)
    
    project_destinationFolder_path = os.path.join(script_dir, DESTINATION_FOLDER)
    
    if not os.path.exists(project_destinationFolder_path):
        # 如果目标文件夹不存在，则创建并执行所有操作
        os.makedirs(project_destinationFolder_path)
        copy_files(project_sourceFolder_path, project_destinationFolder_path)
        generate_project_tree(project_name, project_sourceFolder_path, project_destinationFolder_path)
        generate_project_description(project_purpose, project_prompt, project_destinationFolder_path, {})
    else:
        # 如果目标文件夹已存在，进一步检查_DetailsForAI.txt是否存在
        description_path = os.path.join(project_destinationFolder_path, DESCRIPTION_FILE)
        if os.path.exists(description_path):
            existing_sections = extract_existing_sections(description_path)
            clean_and_copy_files(project_destinationFolder_path, project_sourceFolder_path, project_destinationFolder_path)
            generate_project_tree(project_name, project_sourceFolder_path, project_destinationFolder_path)
            generate_project_description(project_purpose, project_prompt, project_destinationFolder_path, existing_sections)
        else:
            # 如果_DetailsForAI.txt不存在，则正常生成
            copy_files(project_sourceFolder_path, project_destinationFolder_path)
            generate_project_tree(project_name, project_sourceFolder_path, project_destinationFolder_path)
            generate_project_description(project_purpose, project_prompt, project_destinationFolder_path, {})
    
    print("文件复制、项目结构描述和项目描述完成")