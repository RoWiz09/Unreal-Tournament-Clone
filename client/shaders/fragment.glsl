#version 330 core
out vec4 FragColor;

in vec2 TexCoord;
in vec3 FragPos;
in vec3 Normal;

uniform sampler2D texture1; // Color texture
uniform vec3 viewPos;       // Camera position

// Maximum number of lights
const int MAX_LIGHTS = 32;

struct PointLight {
    vec3 position;
    vec3 color;
    float intensity;
    
    float constant;
    float linear;
    float quadratic;
};

uniform int numLights;
uniform PointLight pointLights[MAX_LIGHTS];

void main()
{
    vec3 norm = normalize(Normal);
    vec3 result = vec3(0.0);

    for (int i = 0; i < numLights; i++)
    {
        // Compute the distance and attenuation
        vec3 lightDir = normalize(pointLights[i].position - FragPos);
        float diff = max(dot(norm, lightDir), 0.0);

        // Specular lighting (Phong)
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);

        // Attenuation based on distance
        float distance = length(pointLights[i].position - FragPos);
        float attenuation = 1.0 / (pointLights[i].constant + 
                                pointLights[i].linear * distance + 
                                pointLights[i].quadratic * (distance * distance));

        // Compute final light contribution
        vec3 diffuse = diff * pointLights[i].color * pointLights[i].intensity;
        vec3 specular = spec * pointLights[i].color * 0.5; // Specular strength
        
        result += (diffuse + specular) * attenuation;
    }

    // Apply texture color and combine with lighting
    vec4 textureColor = texture(texture1, TexCoord);
    vec3 finalColor = textureColor.rgb * result;

    FragColor = vec4(finalColor, textureColor.a);
}