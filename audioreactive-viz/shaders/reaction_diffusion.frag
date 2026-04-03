// ─── REACTION-DIFFUSION ───
// params: (feed_rate, kill_rate, diffusion_a, diffusion_b)
// Uses feedback buffer as state (R = chemical A, G = chemical B)

vec2 laplacian(sampler2D tex, vec2 uv, vec2 px) {
    vec2 sum = vec2(0.0);
    // 3x3 convolution kernel
    sum += texture(tex, uv + vec2(-px.x, -px.y)).rg * 0.05;
    sum += texture(tex, uv + vec2(   0., -px.y)).rg * 0.2;
    sum += texture(tex, uv + vec2( px.x, -px.y)).rg * 0.05;
    sum += texture(tex, uv + vec2(-px.x,    0.)).rg * 0.2;
    sum += texture(tex, uv                      ).rg * -1.0;
    sum += texture(tex, uv + vec2( px.x,    0.)).rg * 0.2;
    sum += texture(tex, uv + vec2(-px.x,  px.y)).rg * 0.05;
    sum += texture(tex, uv + vec2(   0.,  px.y)).rg * 0.2;
    sum += texture(tex, uv + vec2( px.x,  px.y)).rg * 0.05;
    return sum;
}

void main() {
    vec2 uv = v_uv;
    vec2 px = 1.0 / u_resolution;

    // Read current state
    vec2 ab = texture(u_feedback, uv).rg;
    float a = ab.x;
    float b = ab.y;

    // Audio-modulated parameters
    float feed = u_params.x + u_bass * 0.015 - u_high * 0.005;
    float kill = u_params.y + u_mid * 0.004;
    float dA = u_params.z;
    float dB = u_params.w;

    // Laplacian diffusion
    vec2 lap = laplacian(u_feedback, uv, px);

    // Gray-Scott reaction
    float reaction = a * b * b;
    float new_a = a + (dA * lap.x - reaction + feed * (1.0 - a));
    float new_b = b + (dB * lap.y + reaction - (kill + feed) * b);

    // Audio seed injection — beats create new chemical spots
    if (u_beat > 0.5) {
        vec2 seed_pos = vec2(
            0.5 + sin(u_time * 1.7) * 0.3,
            0.5 + cos(u_time * 1.3) * 0.3
        );
        float d = length(uv - seed_pos);
        if (d < 0.03 + u_beat * 0.02) {
            new_b = 1.0;
        }
    }

    // Additional seeds from audio peaks
    float rnd = hash21(uv * 100.0 + u_time);
    if (rnd < u_rms * 0.001) {
        new_b = 1.0;
    }

    new_a = clamp(new_a, 0.0, 1.0);
    new_b = clamp(new_b, 0.0, 1.0);

    // Output raw state for ping-pong simulation
    // Colorization happens in a separate pass (colorize_rd.frag)
    fragColor = vec4(new_a, new_b, 0.0, 1.0);
}
