
module alu_tb ;

logic [31:0] in1, in2, out;
logic [2:0] opcode;

initial begin
    in1 = 32'h000005;
    in2 = 32'h000002;
    opcode = 3'b000;
    #10;
    $display("in1: %h, in2: %h, opcode: %b, out: %h", in1, in2, opcode, out);
    opcode = 3'b001;
    #10;
    $display("in1: %h, in2: %h, opcode: %b, out: %h", in1, in2, opcode, out);
    opcode = 3'b100;
    #10;
    $display("in1: %h, in2: %h, opcode: %b, out: %h", in1, in2, opcode, out);
    opcode = 3'b101;
    #10;
    $display("in1: %h, in2: %h, opcode: %b, out: %h", in1, in2, opcode, out);
    opcode = 3'b110;
    #10;
    $display("in1: %h, in2: %h, opcode: %b, out: %h", in1, in2, opcode, out);
    opcode = 3'b111;
    #10;
    $display("in1: %h, in2: %h, opcode: %b, out: %h", in1, in2, opcode, out);
end

alu alu_inst(
    .in1(in1),
    .in2(in2),
    .opcode(opcode),
    .out(out)
);

endmodule