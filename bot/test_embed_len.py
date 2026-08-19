import os
import re

total_commands = 0
total_chars = 0
prefix = ">"

for root, _, files in os.walk('cogs'):
    for file in files:
        if file.endswith('.py'):
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all @commands.command(name="...") or similar
                # Simple approximation: just count def functions with @commands.command
                commands = re.findall(r'@commands\.command\([^)]*\)\s+async def (\w+)', content)
                for cmd in commands:
                    total_commands += 1
                    formatted = f"`{prefix}{cmd}` ・ "
                    total_chars += len(formatted)

print(f"Total commands: {total_commands}")
print(f"Total chars for commands alone: {total_chars}")
