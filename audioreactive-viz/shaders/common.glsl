// ─── Common GLSL utilities ───
// Prepended to all fragment shaders automatically

uniform float u_time;
uniform vec2  u_resolution;
uniform float u_bass;
uniform float u_mid;
uniform float u_high;
uniform float u_rms;
uniform float u_beat;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform vec4  u_params;
uniform float u_feedback_amt;
uniform float u_speed;
uniform sampler2D u_spectrum;
uniform sampler2D u_feedback;

in vec2 v_uv;
out vec4 fragColor;

// ─── Hash / Noise ───

float hash21(vec2 p) {
    p = fract(p * vec2(233.34, 851.74));
    p += dot(p, p + 23.45);
    return fract(p.x * p.y);
}

vec2 hash22(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float noise2d(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(mix(dot(hash22(i + vec2(0,0)), f - vec2(0,0)),
                   dot(hash22(i + vec2(1,0)), f - vec2(1,0)), u.x),
               mix(dot(hash22(i + vec2(0,1)), f - vec2(0,1)),
                   dot(hash22(i + vec2(1,1)), f - vec2(1,1)), u.x), u.y);
}

float fbm(vec2 p, int octaves) {
    float val = 0.0;
    float amp = 0.5;
    float freq = 1.0;
    for (int i = 0; i < 8; i++) {
        if (i >= octaves) break;
        val += amp * noise2d(p * freq);
        freq *= 2.0;
        amp *= 0.5;
    }
    return val;
}

// ─── Utility ───

vec3 palette(float t, vec3 a, vec3 b, vec3 c) {
    return a + (b - a) * smoothstep(0.0, 0.5, t) + (c - b) * smoothstep(0.5, 1.0, t);
}

float sdCircle(vec2 p, float r) {
    return length(p) - r;
}

mat2 rot2(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c);
}
