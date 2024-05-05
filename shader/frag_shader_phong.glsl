#version 330
in vec3 normal;
in vec2 texCoord;
in float useTexture;

in vec3 pos_to_light;
in vec3 pos_to_eye;

uniform sampler2D texture;

uniform vec4 color;
uniform mat4 model;
// uniform vec3 dir_light;

out vec4 outColor;

float k_a = 0.1f;
float k_d = 0.5f;
float k_s = 0.5f;

float shininess = 100;

void main()
{
    vec3 n = normalize(normal);
    
    vec3 pos_to_light_dir = normalize(pos_to_light);
    vec3 pos_to_eye_dir = normalize(pos_to_eye);
    vec3 half = normalize(pos_to_eye_dir + pos_to_light_dir);
    
    float ambient = k_a;
    
    float diffuse = k_d + max(dot(n, pos_to_light_dir), 0.0f);
    
    float glare = dot(n, half);
    float specular = 0.0f;
    if (glare > 0.0f) {
        specular = k_s * pow(dot(n, half), shininess);
    }
    
    float light = ambient + diffuse + specular;
    
    outColor = useTexture > 0.5 ? texture2D(texture, texCoord) : color;
    outColor.xyz *= light;
}