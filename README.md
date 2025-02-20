## AIHELP!!! ##

这是一个可以读取你工作空间里文件的脚本，并让ai辅助修改项目文件：
将.ProjectDescription.yaml, _Script4Overview.py, _Script2Project.py移动到目标文件夹(工作空间)同一目录里
将要读取的文件夹名称按yaml格式添加到target:(在.ProjectDescription.yaml文件内)里，并删除示例文件夹名称
运行_Script4Overview.py脚本文件(将生成文件夹_overview4AI)
将你的需求手动写在_DetailsForAI.txt(在生成的文件夹_overview4AI里)里的NextNeeds部分下并保存
将生成文件夹里的所有文件扔给ai并告诉他它细读Detail里的内容并完成需求
ai将生成一个脚本代码，把这个代码粘贴复制到_Script2Project.py里保存并运行
便可简单实现ai对项目文件的批量修改以达到你的需求
