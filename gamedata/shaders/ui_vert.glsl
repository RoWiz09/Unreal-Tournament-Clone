#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec4 fColor;
out vec2 TexCoord;

uniform mat4 model;
uniform mat4 projection;
uniform vec4 color;
void main()
{
    gl_Position = model * projection * vec4(aPos.x, aPos.y, 0, 1.0);
    fColor = color;
    TexCoord = aTexCoord;
}