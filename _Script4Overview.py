import os
import shutil
import yaml
import platform

class ProjectProcessor:
    def __init__(self, config_path, dest_folder):
        self.__description_file = "_DetailsForAI.txt"
        self.__dest_folder = dest_folder
        
        self.__need_direct = [
            '.txt', '.doc', '.docx', '.pdf','.ppt'
        ]
        self.__need_convert = []
        
        # 初始化时立即读取项目配置
        self.__read_project_description(config_path)


    def __read_project_description(self, file_path):
        """私有方法：读取项目配置文件"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        if data and 'project' in data:
            project = data['project']
            self.__project_name = project.get('name', "未知工程")
            self.__project_purpose = project.get('purpose', "未知目的")
            self.__project_target = project.get('target', [])
            file_types = project.get('file_types', {})
            self.__need_direct = file_types.get('direct', self.__need_direct)
            self.__need_convert = file_types.get('convert', self.__need_convert)
            self.__not_read = project.get('not_read', [])
            # 新增prompt选择逻辑
            prompt_id = project.get('prompt_id', 1)  # 默认使用第一个prompt
            prompts = project.get('prompt', [])      # 默认空列表

            if len(self.__project_target) == 0:
                print("未读取到设置的目标文件夹")
                exit(6)

            # 有效性检查
            if len(prompts) == 0:
                print("未读取到prompt")
            if prompt_id < 1 or prompt_id > len(prompts):
                if len(prompts) == 0:
                    selected_prompt = ""
                else:
                    selected_prompt = prompts[0]
                    print(f"警告：prompt_id {prompt_id} 无效，已使用第一个prompt")
            else:
                selected_prompt = prompts[prompt_id-1]

            self.__project_prompt = selected_prompt


    def __is_interesting_file(self, filename):
        """私有方法：判断文件类型"""
        if any(filename.endswith(ext) for ext in self.__need_direct):
            return 1
        if any(filename.endswith(ext) for ext in self.__need_convert):
            return 2
        return 0

    def __extract_existing_sections(self):
        """私有方法：提取现有内容"""
        existing = {"ProjectDescription": ""}
        desc_path = os.path.join(self.__dest_folder, self.__description_file)
        
        if os.path.exists(desc_path):
            with open(desc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "## ProjectDescription" in content:
                pd_start = content.find("## ProjectDescription")
                pd_end = content.find("---", pd_start)
                existing["ProjectDescription"] = content[pd_start:pd_end]
                
        return existing


    def prepare_workspace(self):
        """准备工作区并执行初始化操作"""
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
            
        self.__clean_workspace()
        self.__copy_files()
        self.__generate_documentation()


    def __clean_workspace(self):
        """清理工作区"""
        for root, dirs, files in os.walk(self.__dest_folder):
            for file in files:
                if file != self.__description_file:
                    os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))


    def __copy_files(self):
        """执行带路径信息的文件复制操作（新增目录过滤）"""
        for src_folder in self.__project_target:
            if not os.path.exists(src_folder):
                print("目标文件夹不存在")
                exit(8)
            for root, dirs, files in os.walk(src_folder):
                # 过滤需要忽略的目录（同时影响子目录遍历）
                dirs[:] = [d for d in dirs if d not in self.__not_read]
                for file in files:
                    file_type = self.__is_interesting_file(file)
                    if file_type not in (1, 2):
                        continue

                    # 生成带路径的文件名
                    relative_path = os.path.relpath(root, src_folder)
                    path_prefix = relative_path.replace(os.sep, '__') + '__' if relative_path != '.' else ''

                    # 构造目标文件名
                    dest_filename = f"{path_prefix}{file}" if file_type == 1 else f"{path_prefix}{file}.txt"
                    dest_path = os.path.join(self.__dest_folder, dest_filename)

                    # 创建目录并复制文件
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(os.path.join(root, file), dest_path)


    def __generate_documentation(self):
        """生成文档结构"""
        self.__generate_project_tree()
        self.__generate_description_content()


    def __generate_project_tree(self):
        """生成项目树结构"""
        path_sep = '/' if platform.system() == 'Linux' else '\\'
        desc_path = os.path.join(self.__dest_folder, self.__description_file)
        not_read = self.__not_read

        def write_tree(folder_path, indent, f):
            try:
                entries = sorted(
                    os.listdir(folder_path), 
                    key=lambda x: (not os.path.isdir(os.path.join(folder_path, x)), x)
                )
            except PermissionError:
                return

            for entry in entries:
                entry_path = os.path.join(folder_path, entry)
                if os.path.isdir(entry_path):
                    if os.path.basename(entry_path) in not_read:
                    # 跳过忽略目录
                        continue
                    f.write(f"{' ' * indent}{os.path.basename(entry_path)}{path_sep}\n")
                    write_tree(entry_path, indent + 4, f)
                elif self.__is_interesting_file(entry):
                    f.write(f"{' ' * indent}{entry}\n")


        with open(desc_path, 'w', encoding='utf-8') as f:
            f.write(f"# {self.__project_name} - 项目结构\n\n## ProjectStructure\n\n")
            f.write(f"{self.__project_name}{path_sep}\n    _Script2Project.py\n")
            for src in self.__project_target:
                if os.path.exists(src):
                    folder_name = os.path.basename(os.path.normpath(src))
                    f.write(f"    {folder_name}{path_sep}\n")
                    write_tree(src, 8, f)
            f.write("\n---\n\n")


    def __generate_description_content(self):
        """生成描述文件内容"""
        existing = self.__extract_existing_sections()
        desc_path = os.path.join(self.__dest_folder, self.__description_file)
        
        with open(desc_path, 'a', encoding='utf-8') as f:
            # ProjectDescription 部分
            if existing["ProjectDescription"]:
                f.write(existing["ProjectDescription"])
            else:
                f.write("\n## ProjectDescription\n\n")
                f.write(f"Environment: {platform.system()}\n\n")
                f.write(f"Information: \n\nPurpose: {self.__project_purpose}\n\nNextNeeds: \n\n")
            f.write("\n---\n\n")
            
            # PromptToAI 部分
            f.write("## PromptToAI\n")
            f.write(f"{self.__project_prompt}")
            f.write("\n---\n\n")



if __name__ == "__main__":
    # 配置常量（可提取到单独配置文件）
    DEST_FOLDER_NAME = '_overview4AI'
    CONFIG_FILE_NAME = '.ProjectDescription.yaml'

    # 路径计算
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, CONFIG_FILE_NAME)
    dest_folder = os.path.join(script_dir, DEST_FOLDER_NAME)

    # 初始化处理器
    try:
        processor = ProjectProcessor(
            config_path,
            dest_folder
        )
    except FileNotFoundError:
        print(f"错误：找不到配置文件 {CONFIG_FILE_NAME}")
        exit(1)
    except Exception as e:
        print(f"配置文件解析错误: {str(e)}")
        exit(2)

    # 构建源路径列表
    source_folders = [
        os.path.normpath(os.path.join(script_dir, f.strip()))
        for f in processor._ProjectProcessor__project_target  # 访问私有变量（实际应通过属性访问）
        if f.strip()  # 过滤空字符串
    ]

    # 验证源文件夹存在
    valid_sources = []
    for folder in source_folders:
        if os.path.exists(folder):
            valid_sources.append(folder)
        else:
            print(f"警告：跳过不存在的源文件夹 {folder}")

    if not valid_sources:
        print("错误：没有有效的源文件夹")
        exit(3)

    # 执行主处理流程
    try:
        processor.prepare_workspace()
        print(f"项目文档生成成功：{dest_folder}")
    except PermissionError as pe:
        print(f"权限错误：{str(pe)}")
        exit(4)
    except Exception as e:
        print(f"处理失败：{str(e)}")
        exit(5)