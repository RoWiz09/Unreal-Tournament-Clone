#version 330 core
out vec4 FragColor;

in vec4 fColor;
in vec2 TexCoord;

uniform sampler2D texture1;
void main()
{
    vec4 textureColor = texture(texture1, TexCoord).rgba;
    FragColor = textureColor * fColor;
} 