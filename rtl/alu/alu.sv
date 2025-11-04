module alu (
    input logic [31:0] in1,
    input logic [31:0] in2,
    input logic [2:0] opcode,
    output logic [31:0] out
);

always_comb begin
    case (opcode)
        3'b000: out = in1 + in2;
        3'b001: out = in1 - in2;
        3'b100: out = in1 & in2;
        3'b101: out = in1 | in2;
        3'b110: out = in1 ^ in2;
        3'b111: out = in1 << in2;
        default: out = 32'b0;
    endcase
end

endmodule