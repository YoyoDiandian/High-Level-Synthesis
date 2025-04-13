#include "parser.h"
#include <iostream>

int main(int argc, char ** argv)
{
    std::ofstream parserOutput("token.txt");
    if(argc != 2)
    {
        parserOutput << "Usage:" << argv[0] << "filename\n";
        parserOutput.close();
        return -1;
    }
    parser p(argv[1]);

    if(p.parse() != 0)
    {
        parserOutput << "parsing error" << p.get_current_line() << std::endl;
        return -1;
    }

    // dump parsed results
    std::vector<basic_block> bbs = p.get_basic_blocks();
    std::string fn_name = p.get_function_name();
    std::vector<var> vars = p.get_function_params();
    int ret_type = p.get_ret_type();

    if(ret_type == RET_INT)
        parserOutput << "ret type: int" << std::endl;
    else
        parserOutput << "ret type: void" << std::endl;

    parserOutput << "function name " << fn_name << std::endl;

    for(int i = 0; i < vars.size(); ++i)
    {
        if(vars[i]._array_flag)
            parserOutput << "array" << std::endl;
        else
            parserOutput << "non-array" << std::endl;
        parserOutput << vars[i]._name << std::endl;
    }

    for(int i = 0; i < bbs.size(); ++i)
    {
        parserOutput << "Basic Block label: " << bbs[i].get_label_name() << std::endl;
        std::vector<statement> ss = bbs[i].get_statements();
        for(int j = 0; j < ss.size(); ++j)
        {
            int type = ss[j].get_type();
            if(type != OP_STORE || type != OP_RET)
            {
                parserOutput << "value " << ss[j].get_var() <<  " " << std::endl;
            }

            parserOutput << "OP TYPE:" <<  ss[j].get_type() << std::endl;
            for(int k = 0; k < ss[j].get_num_oprands(); ++k)
                parserOutput << ss[j].get_oprand(k) << " ";

            parserOutput << std::endl;

        }
    }


}