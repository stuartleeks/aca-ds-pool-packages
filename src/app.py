import asyncio
import os
import tempfile

from anyio import open_file
from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.azure import ACADynamicSessionsCodeExecutor
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


async def main():
    pool_endpoint = os.getenv("ACA_DS_POOL_ENDPOINT", None)
    if pool_endpoint is None:
        raise ValueError(
            "Environment variable ACA_DS_POOL_ENDPOINT is not set.")

    with tempfile.TemporaryDirectory() as temp_dir:
        executor = ACADynamicSessionsCodeExecutor(
            pool_management_endpoint=pool_endpoint,
            credential=DefaultAzureCredential(),
            work_dir=temp_dir
        )
        cancellation_token = CancellationToken()
        
        code_blocks = [
            CodeBlock(code="""
import pkg_resources

# Get the list of installed packages
installed_packages = pkg_resources.working_set
packages_list = sorted(["%s==%s" % (pkg.key, pkg.version) for pkg in installed_packages])

# Save the list to a file named packages.txt
with open("packages.txt", "w") as f:
    f.write("\\n".join(packages_list))

""", language="python")]
        code_result = await executor.execute_code_blocks(code_blocks, cancellation_token)
        print(f"Executed: {code_result}")

        files = await executor.get_file_list(cancellation_token)
        if "packages.txt" not in files:
            raise ValueError("File packages.txt not found in the executor's file list.")
        file_result = await executor.download_files(["packages.txt"], cancellation_token)
        
        print(f"Downloaded: {file_result}")
        async with await open_file(os.path.join(temp_dir, "packages.txt"), "r") as f:
            content = await f.read()
            print(f"======================= packages =======================\n{content}")
        async with await open_file(os.path.join(os.getcwd(), "packages.txt"), "w") as f:
            await f.write(content)
        input("Press Enter to continue...")



asyncio.run(main())
